-- ISO 27701 Batch 3 — Arion posture seed
-- Cross-border transfer + subprocessor discipline. Arion is US-headquartered
-- SaaS with EU customers → Chap V is heavily engaged. Mix reflects mature
-- vendor-management + immature privacy-specific transfer records.

INSERT INTO posture_controls (
    tenant_id, standard_id, control_ref, node_id, finding, confidence,
    gap_description, source, evidence_present, evidence_required, remediation_status
) VALUES
    -- §A.7.5.x controller (4)
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.5.1', 'ISO27701:2019:A.7.5.1',
     'OFI', 'medium',
     'DPA + Standard Contractual Clauses in place with major EU-processing subprocessors (cloud infrastructure). Post-Schrems TIA drafted informally by Legal. No formal transfer basis register; no consolidated per-relationship TIA + supplementary-measures documentation.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.5.2', 'ISO27701:2019:A.7.5.2',
     'OFI', 'medium',
     'Subprocessor list published on the trust page includes countries. No formal destinations register that reconciles against actual PII flows including support-access from other regions.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.5.3', 'ISO27701:2019:A.7.5.3',
     'NC', 'medium',
     'No formal transfer event log for own-controller PII flows (marketing prospects, employee data). Third-party cooperation channels ad hoc; no documented retention period + minimisation applied to records themselves.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.5.4', 'ISO27701:2019:A.7.5.4',
     'NC', 'medium',
     'Investigation + audit disclosures handled ad hoc by Legal. No consolidated disclosure log + source-of-authority not systematically captured across all disclosures.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    -- §B.8.5.x processor (8)
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.5.1', 'ISO27701:2019:B.8.5.1',
     'OFI', 'medium',
     'Standard DPA schedule discloses subprocessor countries + transfer mechanisms (SCCs) at customer onboarding. Customer notifications for new subprocessors sent via trust page updates; no per-customer confirmation SLA + no change-history audit trail per customer.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.5.2', 'ISO27701:2019:B.8.5.2',
     'OFI', 'medium',
     'Subprocessor + country list published on trust page. Formal per-customer disclosure register + support-access destinations not systematically covered.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.5.3', 'ISO27701:2019:B.8.5.3',
     'OFI', 'medium',
     'Customer support-access + integration disclosures logged in Trust ticket system. No consolidated disclosure register; source-of-authority captured inconsistently.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.5.4', 'ISO27701:2019:B.8.5.4',
     'OFI', 'medium',
     'DPA includes 24h notification obligation for legally-binding requests; Legal triages incoming requests. No formal request register + no gag-order protocol documented for cases where notification prohibited by law.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.5.5', 'ISO27701:2019:B.8.5.5',
     'OFI', 'medium',
     'Legal counsel classifies every disclosure request for binding-vs-not. No formal decision register + customer-consultation-before-disclosure not systematically documented.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.5.6', 'ISO27701:2019:B.8.5.6',
     'OFI', 'medium',
     'Subprocessor list on trust page + DPA schedule (updated at onboarding). Pre-use disclosure honoured. No per-customer disclosure register + no formal NDA path for security-sensitive cases.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.5.7', 'ISO27701:2019:B.8.5.7',
     'OFI', 'medium',
     'Written DPAs in place with all subprocessors + Annex B flow-down via ISO 27001 A.5.19 supplier discipline. General customer authorisation via standard DPA clause. No formal engagement register that tracks Annex B coverage + exclusion justifications per subprocessor.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.5.8', 'ISO27701:2019:B.8.5.8',
     'OFI', 'medium',
     'Subprocessor change notifications via trust page updates + 30-day advance notice for material additions. General-authorisation objection handling ad hoc; no formal change register + no documented objection-outcome tracking.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open')
ON CONFLICT DO NOTHING;

SELECT finding, count(*) FROM posture_controls
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND standard_id = 'ISO27701:2019'
GROUP BY finding
ORDER BY finding;
