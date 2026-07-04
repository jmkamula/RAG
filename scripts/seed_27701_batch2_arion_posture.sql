-- ISO 27701 Batch 2 — Arion posture seed
-- Findings reflect a realistic pre-PIMS-certified tenant with mature GDPR
-- programme in place: much OFI (activity exists via GDPR carry-over but not
-- privacy-formalised), some NC (activities entirely missing), 1 N/A.

INSERT INTO posture_controls (
    tenant_id, standard_id, control_ref, node_id, finding, confidence,
    gap_description, source, evidence_present, evidence_required, remediation_status
) VALUES
    -- §A.7.3.x subject rights (controller)
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.1', 'ISO27701:2019:A.7.3.1',
     'OFI', 'medium',
     'GDPR obligations map informally in the DPO''s notes but no consolidated privacy-obligations catalog with per-obligation fulfilment channel + SLA. Contact-point-parity in place (email intake for email-collected PII).',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.2', 'ISO27701:2019:A.7.3.2',
     'OFI', 'medium',
     'Public privacy notice exists with the Art.13 field catalog + indirect-collection additions; layered notice on signup; no formal per-processing-context field-differences map + no automated update-trigger from A.7.2.1 purpose register.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.3', 'ISO27701:2019:A.7.3.3',
     'OFI', 'medium',
     'Notice served at signup + accessible at stable URL. Cookie-banner permits granular consent per purpose. No formal readability target measured; layered notice implemented for the main privacy notice.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.4', 'ISO27701:2019:A.7.3.4',
     'OFI', 'medium',
     'Withdrawal channels functional: cookie preferences per session + email unsubscribe + support-driven for other cases. No documented response-time SLA + propagation-audit not systematic.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.5', 'ISO27701:2019:A.7.3.5',
     'NC', 'medium',
     'Marketing unsubscribe is the only formal objection surface; no procedure for Art.21.1 balancing-test objections against legitimate-interests processing. Notification-of-objection-right in first communication not surfaced explicitly.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.6', 'ISO27701:2019:A.7.3.6',
     'OFI', 'medium',
     'Self-service data-portal supports access + correction; erasure handled via support ticket. No documented undue-delay SLA; no formal refusal-reasoning template. Downstream propagation via manual runbook not automated.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.7', 'ISO27701:2019:A.7.3.7',
     'NC', 'medium',
     'No formal process to notify third parties (recipients of shared PII) when subjects rectify / erase / restrict / object. Third-party recipient inventory not maintained; ad hoc notifications for support-driven cases only.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.8', 'ISO27701:2019:A.7.3.8',
     'OFI', 'medium',
     'Data export available via self-service portal in structured (JSON) format. Not verified to include all PII (edge cases like backend logs / audit trails may not be exported). Direct-transfer (Art.20.2) capability not implemented.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.9', 'ISO27701:2019:A.7.3.9',
     'OFI', 'medium',
     'privacy@ inbox + support-ticket routing handles requests. No formal master register + no SLA-met tracking + no delay-notification protocol when responses exceed Art.12.3 30-day standard.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.3.10', 'ISO27701:2019:A.7.3.10',
     'N/A', 'high',
     'Arion does not perform solely-automated decisions with legal or similarly significant effects. Product surfaces ML-generated findings for HUMAN decision-making by tenants (findings review, posture proposals — always subject to Stage-1/Stage-2 human approval). No Art.22 applicability.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    -- §A.7.4.x privacy by design (controller)
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.1', 'ISO27701:2019:A.7.4.1',
     'OFI', 'medium',
     'Signup forms + cookie banner are minimal (essential only by default; analytics opt-in). No formal necessity-review process for new fields; no consolidated field inventory. Indirect collection (weblogs, cookies) scoped in cookie policy.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.2', 'ISO27701:2019:A.7.4.2',
     'OFI', 'medium',
     'RBAC + role-scoping enforce access limits + tenant isolation via RLS. No formal processing-operation inventory + no default-minimum audit + no side-purpose sweep.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.3', 'ISO27701:2019:A.7.4.3',
     'OFI', 'medium',
     'Self-service correction in tenant portal; input validation on forms. No formal accuracy-incident register; detection driven mostly by subject-reported inaccuracies.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.4', 'ISO27701:2019:A.7.4.4',
     'NC', 'medium',
     'No formal data-minimization objectives defined per activity; no de-identification / pseudonymisation technique catalog. Analytics + ML pipelines use identified PII where anonymisation would be feasible.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.5', 'ISO27701:2019:A.7.4.5',
     'NC', 'medium',
     'No formal end-of-processing trigger detection. Customer offboarding follows the B.8.4.2 return/delete flow (implemented) but for own-controller subjects (marketing prospects, prior employees) no automated cleanup on end-of-processing.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.6', 'ISO27701:2019:A.7.4.6',
     'NC', 'medium',
     'No systematic periodic sweep of temp files in production infrastructure. Application temp files cleaned on service restart but no cadence check + no garbage-collection procedure for filesystem journals + database roll-back files.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.7', 'ISO27701:2019:A.7.4.7',
     'OFI', 'medium',
     'High-level retention policy in the data retention notice (365 days for logs, until account closure for user data). No per-PII-category schedule; no legal/regulatory/business-basis breakdown; no deletion-trigger integration with A.7.4.5.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.8', 'ISO27701:2019:A.7.4.8',
     'OFI', 'medium',
     'Cloud disposal via provider deletion + attestations captured at office decommission; no consolidated disposal register + certificates not centrally tracked. Backup + archive tier disposal follows provider retention policy without org-side verification.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'A.7.4.9', 'ISO27701:2019:A.7.4.9',
     'OFI', 'medium',
     'TLS 1.2+ enforced on customer-facing APIs + integrations; audit logs retained. No consolidated transmission-channel inventory + no shadow-channel sweep (e.g. developers using consumer file-sharing for support cases).',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    -- §B.8.3.1 processor obligations support
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.3.1', 'ISO27701:2019:B.8.3.1',
     'OFI', 'medium',
     'Customer DSAR support handled via Trust ticket + Engineering assist for complex cases; standard DPA covers Art.28.3.e assistance. No formal support-request register + no per-tier SLA matrix.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    -- §B.8.4.x processor PbD
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.4.1', 'ISO27701:2019:B.8.4.1',
     'NC', 'medium',
     'Same as A.7.4.6 — no systematic periodic sweep of temp files in customer-serving infrastructure. Tenant-isolation of temp files enforced by RLS at Postgres level but no verification sweep confirms this holds under load.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.4.2', 'ISO27701:2019:B.8.4.2',
     'OFI', 'medium',
     'Contract-driven data export offered at customer churn (JSON export + attestation of deletion within 90 days). No formal end-of-service register + backup-tier disposal verification not systematic (relies on cloud provider retention).',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open'),
    ('00000000-0000-0000-0000-000000000001', 'ISO27701:2019', 'B.8.4.3', 'ISO27701:2019:B.8.4.3',
     'OFI', 'medium',
     'Customer-facing APIs TLS 1.2+ enforced + mutual-TLS available; subprocessor integrations TLS-encrypted. No formal per-customer channel inventory + customer-consultation-when-silent path not documented.',
     'Not assessed', ARRAY[]::text[], ARRAY[]::text[], 'open')
ON CONFLICT DO NOTHING;

SELECT control_ref, finding, LEFT(gap_description, 60) || '…' AS gap
FROM posture_controls
WHERE tenant_id = '00000000-0000-0000-0000-000000000001'
  AND standard_id = 'ISO27701:2019'
  AND control_ref LIKE 'A.7.3.%' OR (tenant_id = '00000000-0000-0000-0000-000000000001' AND standard_id = 'ISO27701:2019' AND control_ref LIKE 'A.7.4.%')
   OR (tenant_id = '00000000-0000-0000-0000-000000000001' AND standard_id = 'ISO27701:2019' AND control_ref LIKE 'B.8.%')
ORDER BY control_ref;
