# Workbook intake canonical sheet shapes
Taxonomy of curated sheet-shaped leaves. Each entry is a candidate intake YAML; entries marked CLUSTER cover many controls via multi-pass.
**Pending: 340 leaves** (after the 4 done YAMLs).
---
## Tier 1 — Confirmed clusters (one YAML covers many leaves)
### CLUSTER: `program_review_log`  (163 leaves, one canonical YAML)
**Canonical column conventions** (from keyword profile, ≥98% of instances):
- `review_date` — when the review happened (drives freshness vs `freshness_days`)
- `planned_interval` — cadence the review_record claims to track (90/180/365 days)
- `reviewer_identity` — named reviewer (not generic role)
- `scope` — what was reviewed (the linked program / register / control area)
- `findings` / `decisions` — outcome of the review

**Cadence variation**: cadence_days is encoded on the leaf's `freshness_days` (90 for high-volume identity-style reviews, 180 for compliance/supplier, 365 for stable doctrine areas). The YAML's freshness pass uses `column_fingerprint=review_date` and the engine cross-references each leaf's curated freshness_days.

**Naming patterns observed**: `<Domain> Program Review Log` / `<Domain> Annual Review Log`. Fingerprint tokens: `[program, review]`, `[annual, review]`, `[scope, review]`.

**Sample leaves** (full list below):
- `req:4.1:context_program_review` — Context Program Review
- `req:4.2:parties_program_review` — Interested Parties Program Review
- `req:4.3:scope_program_review` — ISMS Scope Program Review
- `req:4.4:isms_program_review` — ISMS Manual Program Review
- `req:5.1:leadership_program_review` — Leadership Program Review
- … (158 more, see appendix)

### CLUSTER: `revocation_log`  (22 leaves, one canonical YAML — possibly 2)
**Canonical column conventions** (≥60% of instances):
- `record_identifier` — unique id per record
- `linked_register` — back-pointer to the parent register (e.g. identity_register → revocation_record links via identity_id)
- `revocation_date` — when the revocation/closure happened
- `authoriser` — named role/person
- `trigger_type` — what caused the revocation (leaver, role change, exit, closure)
- `outcome` — risk-accepted vs returned vs lost

**Variation**: some leaves are 'closure records' (A.5.26 incident-closure) with extra fields like sla_met, root_cause; others are 'asset return' records (A.5.11). May warrant two YAMLs.

**Member leaves**:
- `req:A.5.7:intel_product_record` — Per-Product Intelligence Records
- `req:A.5.8:project_security_closure_record` — Per-Project Security Closure Record
- `req:A.5.11:per_leaver_return_record` — Per-Leaver Asset Return Record
- `req:A.5.13:labelling_application_record` — Per-Platform Labelling Application Record
- `req:A.5.16:identity_revocation_record` — Per-Identity Revocation Record
- `req:A.5.17:credential_revocation_record` — Per-Credential Revocation / Reissue Record
- `req:A.5.18:access_revocation_record` — Access Revocation Records
- `req:A.5.19:offboarding_record` — Supplier Offboarding Records
- `req:A.5.20:deviation_register` — Supplier Agreement Deviation Register
- `req:A.5.21:eol_replacement_record` — ICT Component End-of-Life Replacement Records
- `req:A.5.22:change_response_log` — Supplier Service Change Response Log
- `req:A.5.23:exit_migration_record` — Cloud Service Exit / Migration Records
- `req:A.5.24:framework_exercise_record` — Per-Exercise Framework Activation Record
- `req:A.5.25:triage_decision_record` — Per-Event Triage Decision Records
- `req:A.5.26:incident_closure_record` — Per-Incident Closure Records
- `req:A.5.27:improvement_action_record` — Per-Lesson Improvement Action Records
- `req:A.5.28:evidence_disposal_record` — Per-Package Evidence Disposal / Handover Record
- `req:A.5.29:plan_activation_record` — Per-Activation Plan Record
- `req:A.5.30:ict_recovery_record` — Per-Recovery Event Record
- `req:A.5.35:finding_response_register` — Independent Review Finding Response Register
- `req:A.5.36:nonconformity_register` — Compliance Nonconformity Register
- `req:A.7.14:disposal_record` — Per-Equipment Disposal Record

## Tier 2 — Small clusters (2-10 leaves, one YAML each)
### `monitoring_record`  (6 leaves)
- `req:A.8.2:privileged_activity_log` — Privileged Activity Log
- `req:A.8.4:source_code_monitoring_log` — Source Code Access Monitoring Log
- `req:A.8.5:authentication_log` — Authentication Activity Log
- `req:A.8.6:capacity_monitoring_log` — Capacity Monitoring Log
- `req:A.8.12:dlp_alert_log` — DLP Alert Log
- `req:A.8.14:failover_test_register` — Failover Test Register

### `change_record`  (3 leaves)
- `req:4.3:scope_change_record` — ISMS Scope Change Record
- `req:4.4:isms_manual_change_record` — ISMS Manual Change Record
- `req:5.3:isms_roles_change_record` — ISMS Roles Change Record

### `responsibility_matrix`  (2 leaves)
- `req:5.3:isms_roles_authorities` — ISMS Roles, Responsibilities and Authorities Matrix
- `req:A.5.2:roles_and_responsibilities` — Information Security Roles and Responsibilities Matrix

### `contact_register`  (2 leaves)
- `req:A.5.5:authority_contact_register` — Authority Contact Register
- `req:A.5.6:special_interest_group_register` — Special Interest Group and Professional Forum Register

## Tier 3 — Registers (124 leaves, mostly unique sheet shapes)
Each register is a distinct real-world artefact with its own column conventions — **likely one YAML per leaf** rather than a shared canonical shape. Listed by standard / control for navigation; prioritise via the high-value tier (below).

### ISO27001 / A.5 (Organisational)  (24 register YAMLs)
- `req:A.5.7:threat_intel_feed_register` (7 MUSTs, 2 SHOULDs) — Threat Intelligence Feed Register
- `req:A.5.8:project_security_register` (7 MUSTs, 2 SHOULDs) — Project Security Register
- `req:A.5.11:leaver_return_register` (7 MUSTs, 2 SHOULDs) — Leaver Asset Return Register
- `req:A.5.13:labelling_coverage_register` (7 MUSTs, 2 SHOULDs) — Labelling Coverage Register
- `req:A.5.16:identity_register` (8 MUSTs, 2 SHOULDs) — Identity Register
- `req:A.5.17:credential_register` (7 MUSTs, 2 SHOULDs) — Credential Register
- `req:A.5.19:supplier_register` (5 MUSTs, 2 SHOULDs) — Supplier Register
- `req:A.5.20:coverage_register` (5 MUSTs, 2 SHOULDs) — Supplier Agreement Coverage Register
- `req:A.5.21:ict_component_register` (5 MUSTs, 2 SHOULDs) — ICT Component / Vendor Register
- `req:A.5.22:review_schedule_register` (4 MUSTs, 2 SHOULDs) — Supplier Review Schedule Register
- `req:A.5.23:cloud_service_register` (7 MUSTs, 3 SHOULDs) — Cloud Service Register
- `req:A.5.24:incident_response_team_register` (7 MUSTs, 2 SHOULDs) — Incident Response Team Register
- `req:A.5.25:event_triage_log` (5 MUSTs, 2 SHOULDs) — Security Event Triage Log
- `req:A.5.27:lessons_register` (7 MUSTs, 2 SHOULDs) — Lessons Learned Register
- `req:A.5.28:evidence_custody_register` (8 MUSTs, 2 SHOULDs) — Evidence Custody Register
- `req:A.5.29:disruption_scenario_register` (7 MUSTs, 2 SHOULDs) — Disruption Scenario Register
- `req:A.5.30:ict_service_register` (7 MUSTs, 2 SHOULDs) — ICT Service Continuity Register
- `req:A.5.31:legal_regulatory_register` (7 MUSTs, 3 SHOULDs) — Legal, Statutory, Regulatory and Contractual Requirements Register
- `req:A.5.32:licensed_software_ipr_inventory` (5 MUSTs, 2 SHOULDs) — Licensed Software and IPR Inventory
- `req:A.5.33:records_schedule_register` (7 MUSTs, 3 SHOULDs) — Records Schedule (Per-Class Retention and Protection Register)
- `req:A.5.34:pii_processing_register` (8 MUSTs, 3 SHOULDs) — PII Processing Register
- `req:A.5.35:review_schedule_register` (6 MUSTs, 2 SHOULDs) — Independent Review Schedule Register
- `req:A.5.36:compliance_review_schedule` (6 MUSTs, 2 SHOULDs) — Compliance Review Schedule
- `req:A.5.37:operating_procedures_register` (6 MUSTs, 3 SHOULDs) — Documented Operating Procedures Register

### ISO27001 / A.6 (People)  (7 register YAMLs)
- `req:A.6.1:screening_record_register` (6 MUSTs, 2 SHOULDs) — Per-Candidate Screening Record Register
- `req:A.6.2:signed_terms_register` (5 MUSTs, 2 SHOULDs) — Signed Employment Terms Register
- `req:A.6.3:training_completion_register` (6 MUSTs, 2 SHOULDs) — Training Completion Register
- `req:A.6.4:disciplinary_case_register` (6 MUSTs, 2 SHOULDs) — Disciplinary Case Register
- `req:A.6.5:leaver_briefing_register` (6 MUSTs, 2 SHOULDs) — Leaver Briefing Register
- `req:A.6.6:nda_signature_register` (6 MUSTs, 2 SHOULDs) — NDA Signature Register
- `req:A.6.8:event_report_register` (7 MUSTs, 2 SHOULDs) — Event Report Register

### ISO27001 / A.7 (Physical)  (13 register YAMLs)
- `req:A.7.1:perimeter_register` (5 MUSTs, 1 SHOULDs) — Per-Site Perimeter Register
- `req:A.7.2:entry_event_register` (5 MUSTs, 1 SHOULDs) — Physical Entry Event Register
- `req:A.7.3:room_register` (5 MUSTs, 1 SHOULDs) — Room Register
- `req:A.7.4:monitoring_event_register` (5 MUSTs, 1 SHOULDs) — Monitoring Event Register
- `req:A.7.5:threat_register` (5 MUSTs, 1 SHOULDs) — Per-Site Threat Register
- `req:A.7.6:work_session_register` (5 MUSTs, 1 SHOULDs) — Secure Area Work Session Register
- `req:A.7.7:cd_cs_audit_register` (5 MUSTs, 1 SHOULDs) — Clear Desk / Clear Screen Audit Register
- `req:A.7.8:siting_register` (5 MUSTs, 1 SHOULDs) — Equipment Siting Register
- `req:A.7.9:off_premises_register` (5 MUSTs, 1 SHOULDs) — Off-Premises Asset Register
- `req:A.7.10:media_register` (5 MUSTs, 1 SHOULDs) — Storage Media Register
- `req:A.7.11:utility_register` (5 MUSTs, 1 SHOULDs) — Per-Site Utility Register
- `req:A.7.12:cabling_register` (5 MUSTs, 1 SHOULDs) — Cabling Run Register
- `req:A.7.13:maintenance_event_register` (6 MUSTs, 1 SHOULDs) — Maintenance Event Register

### ISO27001 / A.8 (Technological)  (28 register YAMLs)
- `req:A.8.1:endpoint_register` (5 MUSTs, 1 SHOULDs) — Endpoint Inventory Register
- `req:A.8.3:access_matrix_register` (5 MUSTs, 1 SHOULDs) — Per-System Access Matrix Register
- `req:A.8.7:malware_coverage_register` (5 MUSTs, 1 SHOULDs) — Malware Protection Coverage Register
- `req:A.8.8:vulnerability_backlog_register` (6 MUSTs, 1 SHOULDs) — Vulnerability Backlog Register
- `req:A.8.9:configuration_baseline_register` (5 MUSTs, 1 SHOULDs) — Configuration Baseline Register
- `req:A.8.10:deletion_register` (6 MUSTs, 1 SHOULDs) — Per-Deletion Disposal Register
- `req:A.8.11:masking_register` (5 MUSTs, 1 SHOULDs) — Per-Dataset Masking Register
- `req:A.8.13:restore_test_register` (6 MUSTs, 1 SHOULDs) — Restore Test Register
- `req:A.8.15:log_source_register` (5 MUSTs, 1 SHOULDs) — Log Source Register
- `req:A.8.16:detection_register` (5 MUSTs, 1 SHOULDs) — Detection Use-Case Register
- `req:A.8.17:sync_register` (4 MUSTs, 1 SHOULDs) — Clock Sync Status Register
- `req:A.8.18:utility_register` (5 MUSTs, 1 SHOULDs) — Privileged Utility Programs Register
- `req:A.8.19:installation_register` (5 MUSTs, 1 SHOULDs) — Software Installation Register
- `req:A.8.20:network_register` (5 MUSTs, 1 SHOULDs) — Network Inventory Register
- `req:A.8.21:service_register` (5 MUSTs, 1 SHOULDs) — Network Services Register
- `req:A.8.22:zone_register` (5 MUSTs, 1 SHOULDs) — Network Zone Register
- `req:A.8.23:filtering_event_register` (4 MUSTs, 1 SHOULDs) — Web Filtering Event Register
- `req:A.8.24:key_register` (6 MUSTs, 1 SHOULDs) — Cryptographic Key Register
- `req:A.8.25:project_register` (5 MUSTs, 1 SHOULDs) — Development Project Register
- `req:A.8.26:application_register` (5 MUSTs, 1 SHOULDs) — Application Security Requirements Register
- `req:A.8.27:architecture_register` (5 MUSTs, 1 SHOULDs) — Reference Architecture Register
- `req:A.8.28:finding_register` (5 MUSTs, 1 SHOULDs) — Secure Coding Finding Register
- `req:A.8.29:test_register` (6 MUSTs, 1 SHOULDs) — Security Test Register
- `req:A.8.30:engagement_register` (6 MUSTs, 1 SHOULDs) — Outsourced Development Engagement Register
- `req:A.8.31:environment_register` (5 MUSTs, 1 SHOULDs) — Environment Register
- `req:A.8.32:change_register` (6 MUSTs, 1 SHOULDs) — Change Register
- `req:A.8.33:test_dataset_register` (6 MUSTs, 1 SHOULDs) — Test Dataset Register
- `req:A.8.34:audit_engagement_register` (6 MUSTs, 1 SHOULDs) — Audit Testing Engagement Register

### ISO27001 / ISMS clauses  (14 register YAMLs)
- `req:4.1:context_issues_register` (6 MUSTs, 1 SHOULDs) — Internal and External Issues Register
- `req:4.2:interested_parties_register` (6 MUSTs, 1 SHOULDs) — Interested Parties and Requirements Register
- `req:6.1.1:planned_action_register` (6 MUSTs, 1 SHOULDs) — ISMS Planned Action Register
- `req:6.2:security_objectives_register` (6 MUSTs, 1 SHOULDs) — Information Security Objectives Register
- `req:6.3:isms_change_register` (6 MUSTs, 1 SHOULDs) — ISMS Change Register
- `req:7.1:isms_resources_record` (6 MUSTs, 1 SHOULDs) — ISMS Resource Allocation Record
- `req:7.2:competence_record` (6 MUSTs, 1 SHOULDs) — ISMS Competence Record
- `req:7.3:awareness_completion_register` (5 MUSTs, 1 SHOULDs) — ISMS Awareness Completion Register
- `req:7.4:communication_event_register` (6 MUSTs, 1 SHOULDs) — ISMS Communication Event Register
- `req:7.5:isms_document_register` (7 MUSTs, 1 SHOULDs) — ISMS Document Register
- `req:8.1:operational_execution_register` (5 MUSTs, 1 SHOULDs) — Operational Execution Register
- `req:9.1:measurement_record` (6 MUSTs, 1 SHOULDs) — ISMS Measurement Record
- `req:10.1:improvement_action_register` (7 MUSTs, 1 SHOULDs) — Improvement Action Register
- `req:10.2:nonconformity_register` (8 MUSTs, 1 SHOULDs) — Nonconformity Register

### GDPR  (38 register YAMLs)
- `req:Art.7:consent_register` (6 MUSTs, 1 SHOULDs) — Consent Register
- `req:Art.8:child_consent_register` (5 MUSTs, 1 SHOULDs) — Child Consent Register
- `req:Art.9:special_category_processing_register` (6 MUSTs, 1 SHOULDs) — Special Category Processing Register
- `req:Art.10:criminal_data_processing_register` (5 MUSTs, 1 SHOULDs) — Criminal Data Processing Register
- `req:Art.12:rights_request_register` (6 MUSTs, 1 SHOULDs) — Rights Request Register
- `req:Art.14:source_register` (5 MUSTs, 1 SHOULDs) — Art.14 Source Register
- `req:Art.15:dsar_register` (6 MUSTs, 2 SHOULDs) — DSAR Register
- `req:Art.16:rectification_register` (5 MUSTs, 1 SHOULDs) — Rectification Request Register
- `req:Art.17:erasure_register` (6 MUSTs, 1 SHOULDs) — Erasure Request Register
- `req:Art.18:restriction_register` (5 MUSTs, 1 SHOULDs) — Restriction Register
- `req:Art.19:notification_register` (4 MUSTs, 1 SHOULDs) — Recipient Notification Register
- `req:Art.20:portability_register` (5 MUSTs, 1 SHOULDs) — Portability Request Register
- `req:Art.21:objection_register` (5 MUSTs, 1 SHOULDs) — Objection Register
- `req:Art.22:automated_decision_register` (5 MUSTs, 1 SHOULDs) — Automated Decision-Making Register
- `req:Art.23:restriction_register` (5 MUSTs, 1 SHOULDs) — Art.23 Restriction Application Register
- `req:Art.24:gdpr_compliance_register` (6 MUSTs, 1 SHOULDs) — GDPR Compliance Register
- `req:Art.26:joint_controller_register` (5 MUSTs, 1 SHOULDs) — Joint Controller Register
- `req:Art.27:representative_operations_record` (5 MUSTs, 1 SHOULDs) — Representative Operations Record
- `req:Art.28:processor_register` (5 MUSTs, 1 SHOULDs) — Per-Processor DPA Register
- `req:Art.29:personnel_authorisation_register` (4 MUSTs, 1 SHOULDs) — Personnel Authorisation Register
- `req:Art.31:interaction_register` (6 MUSTs, 1 SHOULDs) — SA Interaction Register
- `req:Art.32:risk_appropriate_measures_register` (5 MUSTs, 1 SHOULDs) — Risk-Appropriate Measures Register (Art.32.1)
- `req:Art.34:subject_communication_record` (6 MUSTs, 1 SHOULDs) — Subject Communication Record
- `req:Art.35:dpia_register` (6 MUSTs, 1 SHOULDs) — DPIA Register
- `req:Art.36:consultation_register` (6 MUSTs, 1 SHOULDs) — Prior Consultation Register
- `req:Art.37:designation_record` (5 MUSTs, 1 SHOULDs) — DPO Designation Record
- `req:Art.38:position_evidence_register` (5 MUSTs, 1 SHOULDs) — DPO Position Evidence Register
- `req:Art.39:dpo_activity_register` (5 MUSTs, 1 SHOULDs) — DPO Activity Register
- `req:Art.40:adherence_register` (5 MUSTs, 1 SHOULDs) — Code Adherence Register
- `req:Art.41:monitoring_record` (5 MUSTs, 1 SHOULDs) — Code Monitoring Activity Record
- `req:Art.42:certification_register` (5 MUSTs, 1 SHOULDs) — Certification Register
- `req:Art.43:certification_issuance_record` (5 MUSTs, 1 SHOULDs) — Certification Issuance Record
- `req:Art.44:transfer_register` (6 MUSTs, 1 SHOULDs) — International Transfer Register
- `req:Art.45:adequacy_register` (4 MUSTs, 1 SHOULDs) — Adequacy Reliance Register
- `req:Art.46:safeguards_register` (6 MUSTs, 1 SHOULDs) — Safeguards Register
- `req:Art.47:bcr_register` (5 MUSTs, 1 SHOULDs) — BCR Coverage Register
- `req:Art.48:foreign_request_register` (5 MUSTs, 1 SHOULDs) — Foreign Authority Request Register
- `req:Art.49:invocation_register` (5 MUSTs, 1 SHOULDs) — Derogation Invocation Register

## Tier 4 — One-off shapes (distinct evidence_types, 1 leaf each)
Each is a unique sheet shape — author one bespoke YAML per leaf. Most are high-value (RoPA, SoA, audit programme, classification scheme).

- **approval_record** — `req:5.2:isp_approval_record` — Information Security Policy Approval Record  (4 MUSTs)
- **audit_programme** — `req:9.2:internal_audit_programme` — Internal Audit Programme  (7 MUSTs)
- **audit_record** — `req:9.2:audit_execution_record` — Internal Audit Execution Record  (6 MUSTs)
- **classification_scheme** — `req:A.5.12:information_classification_scheme` — Information Classification Scheme  (6 MUSTs)
- **configuration_record** — `req:Art.25:default_settings_record` — Privacy-default configuration record (Art.25.2)  (5 MUSTs)
- **data_flow_inventory** — `req:Art.30:data_flow_inventory` — Personal Data Flow Inventory  (5 MUSTs)
- **decision_record** — `req:Art.24:controller_processor_decision_record` — Controller / Processor Role Decision Record  (5 MUSTs)
- **discovery_record** — `req:A.5.9:asset_discovery_upstream` — Asset Discovery and Onboarding Upstream  (4 MUSTs)
- **lawful_basis_register** — `req:Art.6:lawful_basis_register` — Lawful Basis Register (Art.6)  (6 MUSTs)
- **publication_record** — `req:Art.13:publication_record` — Privacy Notice Publication Record  (5 MUSTs)
- **records_of_processing** — `req:Art.30:records_of_processing` — Records of Processing Activities (RoPA)  (9 MUSTs)
- **risk_assessment** — `req:6.1.2:risk_assessment` — Information Security Risk Assessment Procedure  (8 MUSTs)
- **risk_assessment_record** — `req:8.2:operational_risk_assessment_record` — Operational Risk Assessment Records  (6 MUSTs)
- **risk_treatment_plan** — `req:6.1.3:risk_treatment_plan` — Risk Treatment Plan  (6 MUSTs)
- **risk_treatment_record** — `req:8.3:operational_risk_treatment_record` — Operational Risk Treatment Records  (6 MUSTs)
- **segregation_matrix** — `req:A.5.3:segregation_of_duties` — Segregation of Duties Matrix  (5 MUSTs)
- **statement_of_applicability** — `req:6.1.3:statement_of_applicability` — Statement of Applicability  (7 MUSTs)
- **test_log** — `req:Art.32:resilience_test` — Periodic resilience and restoration test record  (3 MUSTs)

## Suggested authoring sequence
1. **Batch 1 (high leverage)** — the `program_review_log` cluster YAML (closes 163 leaves at once).
2. **Batch 2 (high value)** — Tier 4 one-offs aligned to ISMS clauses 9 + 10 (audit_programme, statement_of_applicability, risk_treatment_plan, RoPA, etc.) and GDPR cross-framework artefacts (data_flow_inventory, lawful_basis_register).
3. **Batch 3 (close the lifecycle-end family)** — revocation_record cluster (22 leaves) + change_record (3) + monitoring_record (6) + small Tier 2 entries.
4. **Batches 4-N (per-section register sweep)** — iterate registers section by section (A.5, A.6, A.7, A.8, ISMS, GDPR). Each batch ~10-20 register YAMLs.
