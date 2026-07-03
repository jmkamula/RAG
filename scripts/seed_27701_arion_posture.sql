-- ISO 27701 Batch 1 — Arion posture seed
--
-- Arion is BOTH controller AND processor per client_facts, so all 14
-- Batch 1 controls apply. Findings reflect a realistic pre-PIMS-certified
-- tenant: some OFI from GDPR programme carry-over, some NC where the
-- privacy-specific programme is missing, one N/A (no joint controller
-- arrangements).

INSERT INTO posture_controls (
    tenant_id, standard_id, control_ref, node_id, finding, confidence,
    gap_description, source, evidence_present, evidence_required,
    remediation_status
) VALUES
    -- Controller side §A.7.2.x
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.2.1', 'ISO27701:2019:A.7.2.1',
     'OFI', 'medium',
     'Purposes for PII processing are informally documented in the privacy notice and DPAs, but no central purpose register exists yet. Each product surface treats purpose separately, so specificity and cross-activity consistency drift.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.2.2', 'ISO27701:2019:A.7.2.2',
     'OFI', 'medium',
     'GDPR Art.6 basis is assessed per processing activity but no consolidated lawful basis register; legitimate-interests balancing tests are drafted ad hoc without a standardised LIA template.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.2.3', 'ISO27701:2019:A.7.2.3',
     'OFI', 'medium',
     'Consent-collection artefacts (web forms, cookie banner, marketing opt-ins) exist but there is no documented procedure defining when consent is required, the quality standard, or non-bundling rules.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.2.4', 'ISO27701:2019:A.7.2.4',
     'OFI', 'medium',
     'Consent events are captured in application logs for cookie preferences and marketing opt-ins, but the retrieval + demonstration pathway is not stated as an SLA and consent-artifact versioning is inconsistent.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.2.5', 'ISO27701:2019:A.7.2.5',
     'NC', 'medium',
     'No formal PIA/DPIA program in place. Individual DPIAs have been performed ad hoc when engineering flags new high-risk processing, but the trigger criteria, template, and register are not documented. Art.35.3 mandatory-DPIA scope not formally mapped.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.2.6', 'ISO27701:2019:A.7.2.6',
     'OFI', 'medium',
     'DPAs are signed with major processors (cloud infrastructure, SaaS vendors) using a standard template. However, the processor register is not centrally maintained and Annex B / Art.28.3 coverage is not audited per contract.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.2.7', 'ISO27701:2019:A.7.2.7',
     'N/A', 'high',
     'No joint PII controller arrangements. All processing is either sole-controller (Arion determines purposes and means) or controller-processor (Arion as processor for customer PII).',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.2.8', 'ISO27701:2019:A.7.2.8',
     'OFI', 'medium',
     'A rudimentary records of processing exists in the privacy office spreadsheet, covering major activities. However, coverage is incomplete (missing recent product launches), Art.30.1 field coverage is uneven, and no formal owner or annual review cadence.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    -- Processor side §B.8.2.x
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.2.1', 'ISO27701:2019:B.8.2.1',
     'OFI', 'medium',
     'Standard customer DPA is executed with enterprise + business tier customers via the order form. Startup tier customers accept a click-through DPA. Assistance obligations (Art.28.3.e-h) are covered but customer-tier coverage matrix is not maintained.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.2.2', 'ISO27701:2019:B.8.2.2',
     'OFI', 'medium',
     'Customer PII is technically isolated via multi-tenant boundaries (tenant_id enforced by RLS + application-level scoping). No formal cross-tenant analytics / ML training uses customer PII. However, no documented technical-binding audit + no formal customer-verification pathway.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.2.3', 'ISO27701:2019:B.8.2.3',
     'NC', 'medium',
     'No formal marketing / advertising prohibition procedure exists for customer PII, and no exception register. Marketing systems currently use own-controller data only, but the compliance framing + audit trail is missing.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.2.4', 'ISO27701:2019:B.8.2.4',
     'NC', 'medium',
     'No formal procedure exists to inform customers when a processing instruction may infringe legislation. Support + Legal have handled ad hoc cases but there is no captured notification format, escalation path, or historical register.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.2.5', 'ISO27701:2019:B.8.2.5',
     'OFI', 'medium',
     'SOC 2 Type II report + ISO 27001 certification are shared with customers under NDA on request. Individual audit requests handled ad hoc by Trust team. No documented audit-tier matrix, no request register, no formal SLA.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.2.6', 'ISO27701:2019:B.8.2.6',
     'OFI', 'medium',
     'Processor-side records exist per major customer (categories of processing, subprocessor list) as part of the DPA package. However, Art.30.2 field coverage is inconsistent and there is no annual reconciliation against the customer register.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open')
ON CONFLICT DO NOTHING;

-- Show what was inserted
SELECT control_ref, finding, LEFT(gap_description, 60) || '…' AS gap
FROM posture_controls
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND standard_id = 'ISO27701:2019'
ORDER BY control_ref;
