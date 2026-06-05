# Workbook intake YAML inventory

**Counts:** 344 sheet-shaped leaves total · 4 done · 340 pending · 163 of pending are review_record borderline cases.

Enumeration of sheet-shaped `EvidenceRequirement` leaves from the curated
set (`enrichment/documents/document_requirements.py`). Each sheet-shaped
leaf is a candidate target for a `db/workbook_mappings/*.yaml` intake
mapping. Doc-shaped leaves (policy / procedure / plan / report / minutes /
agreement) are NOT YAML targets — they come through file upload + LLM
doc extraction.

Per the README §1, one YAML covers one canonical sheet shape and may bind
multiple `(control × leaf)` targets via separate passes. So this is the
**upper bound** of YAMLs needed — some leaves below may consolidate into a
single multi-pass YAML where their sheet shape is genuinely shared.

## ISO27001:2022

### 4.1

- `req:4.1:context_issues_register` (register) — Internal and External Issues Register
- `req:4.1:context_program_review` (review_record) — Context Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 4.2

- `req:4.2:interested_parties_register` (register) — Interested Parties and Requirements Register
- `req:4.2:parties_program_review` (review_record) — Interested Parties Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 4.3

- `req:4.3:scope_change_record` (change_record) — ISMS Scope Change Record
- `req:4.3:scope_program_review` (review_record) — ISMS Scope Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 4.4

- `req:4.4:isms_manual_change_record` (change_record) — ISMS Manual Change Record
- `req:4.4:isms_program_review` (review_record) — ISMS Manual Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 5.1

- `req:5.1:leadership_reaffirmation_record` (review_record) — Leadership Reaffirmation Record  ⚠️ borderline (review_record — register-style or minutes?)
- `req:5.1:leadership_program_review` (review_record) — Leadership Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 5.2

- `req:5.2:isp_approval_record` (approval_record) — Information Security Policy Approval Record
- `req:5.2:isp_program_review` (review_record) — Information Security Policy Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 5.3

- `req:5.3:isms_roles_authorities` (responsibility_matrix) — ISMS Roles, Responsibilities and Authorities Matrix
- `req:5.3:isms_roles_change_record` (change_record) — ISMS Roles Change Record
- `req:5.3:isms_roles_program_review` (review_record) — ISMS Roles Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 6.1.1

- `req:6.1.1:planned_action_register` (register) — ISMS Planned Action Register
- `req:6.1.1:planning_program_review` (review_record) — Planning Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 6.1.2

- `req:6.1.2:risk_assessment` (risk_assessment) — Information Security Risk Assessment Procedure
- `req:6.1.2:risk_register` (register) — Information Security Risk Register  ✅ done → `risk_register.yaml`
- `req:6.1.2:risk_assessment_program_review` (review_record) — Risk Assessment Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 6.1.3

- `req:6.1.3:risk_treatment_plan` (risk_treatment_plan) — Risk Treatment Plan
- `req:6.1.3:statement_of_applicability` (statement_of_applicability) — Statement of Applicability
- `req:6.1.3:risk_treatment_program_review` (review_record) — Risk Treatment Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 6.2

- `req:6.2:security_objectives_register` (register) — Information Security Objectives Register
- `req:6.2:objectives_program_review` (review_record) — Objectives Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 6.3

- `req:6.3:isms_change_register` (register) — ISMS Change Register
- `req:6.3:change_program_review` (review_record) — ISMS Change Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 7.1

- `req:7.1:isms_resources_record` (register) — ISMS Resource Allocation Record
- `req:7.1:resources_program_review` (review_record) — Resources Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 7.2

- `req:7.2:competence_record` (register) — ISMS Competence Record
- `req:7.2:competence_program_review` (review_record) — Competence Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 7.3

- `req:7.3:awareness_completion_register` (register) — ISMS Awareness Completion Register
- `req:7.3:awareness_program_review` (review_record) — Awareness Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 7.4

- `req:7.4:communication_event_register` (register) — ISMS Communication Event Register
- `req:7.4:communication_program_review` (review_record) — Communication Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 7.5

- `req:7.5:isms_document_register` (register) — ISMS Document Register
- `req:7.5:document_control_program_review` (review_record) — Document Control Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 8.1

- `req:8.1:operational_execution_register` (register) — Operational Execution Register
- `req:8.1:operational_planning_program_review` (review_record) — Operational Planning Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 8.2

- `req:8.2:operational_risk_assessment_record` (risk_assessment_record) — Operational Risk Assessment Records
- `req:8.2:operational_assessment_program_review` (review_record) — Operational Assessment Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 8.3

- `req:8.3:operational_risk_treatment_record` (risk_treatment_record) — Operational Risk Treatment Records
- `req:8.3:treatment_execution_program_review` (review_record) — Treatment Execution Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 9.1

- `req:9.1:measurement_record` (register) — ISMS Measurement Record
- `req:9.1:monitoring_program_review` (review_record) — Monitoring Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 9.2

- `req:9.2:internal_audit_programme` (audit_programme) — Internal Audit Programme
- `req:9.2:audit_execution_record` (audit_record) — Internal Audit Execution Record
- `req:9.2:audit_program_review` (review_record) — Audit Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 9.3

- `req:9.3:management_review_program_review` (review_record) — Management Review Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 10.1

- `req:10.1:improvement_action_register` (register) — Improvement Action Register
- `req:10.1:improvement_program_review` (review_record) — Continual Improvement Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### 10.2

- `req:10.2:nonconformity_register` (register) — Nonconformity Register
- `req:10.2:nc_program_review` (review_record) — NC/CA Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.1

- `req:A.5.1:annual_review` (review_record) — Periodic Information Security Policy Review Record  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.2

- `req:A.5.2:roles_and_responsibilities` (responsibility_matrix) — Information Security Roles and Responsibilities Matrix
- `req:A.5.2:annual_review` (review_record) — Periodic Roles and Responsibilities Review Record  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.3

- `req:A.5.3:segregation_of_duties` (segregation_matrix) — Segregation of Duties Matrix
- `req:A.5.3:periodic_review` (review_record) — Periodic Segregation of Duties Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.4

- `req:A.5.4:periodic_review` (review_record) — Periodic Review of the Management Directive  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.5

- `req:A.5.5:authority_contact_register` (contact_register) — Authority Contact Register
- `req:A.5.5:authority_contact_review` (review_record) — Periodic Authority Contact Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.6

- `req:A.5.6:special_interest_group_register` (contact_register) — Special Interest Group and Professional Forum Register
- `req:A.5.6:sig_engagement_review` (review_record) — Periodic SIG Engagement Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.7

- `req:A.5.7:threat_intel_feed_register` (register) — Threat Intelligence Feed Register
- `req:A.5.7:threat_intel_program_review` (review_record) — Periodic Threat Intelligence Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.7:intel_product_record` (revocation_record) — Per-Product Intelligence Records

### A.5.8

- `req:A.5.8:project_security_register` (register) — Project Security Register
- `req:A.5.8:project_security_program_review` (review_record) — Periodic Project-Security Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.8:project_security_closure_record` (revocation_record) — Per-Project Security Closure Record

### A.5.9

- `req:A.5.9:asset_inventory` (asset_register) — Inventory of Information and Associated Assets  ✅ done → `asset_register.yaml`
- `req:A.5.9:asset_discovery_upstream` (discovery_record) — Asset Discovery and Onboarding Upstream
- `req:A.5.9:asset_reconciliation_review` (review_record) — Periodic Asset Inventory Reconciliation  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.10

- `req:A.5.10:periodic_review` (review_record) — Periodic Acceptable Use Policy Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.11

- `req:A.5.11:leaver_return_register` (register) — Leaver Asset Return Register
- `req:A.5.11:return_program_review` (review_record) — Periodic Asset-Return Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.11:per_leaver_return_record` (revocation_record) — Per-Leaver Asset Return Record

### A.5.12

- `req:A.5.12:information_classification_scheme` (classification_scheme) — Information Classification Scheme
- `req:A.5.12:periodic_review` (review_record) — Periodic Classification Scheme Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.13

- `req:A.5.13:labelling_coverage_register` (register) — Labelling Coverage Register
- `req:A.5.13:labelling_program_review` (review_record) — Periodic Labelling Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.13:labelling_application_record` (revocation_record) — Per-Platform Labelling Application Record

### A.5.14

- `req:A.5.14:periodic_review` (review_record) — Periodic Information Transfer Policy Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.15

- `req:A.5.15:periodic_review` (review_record) — Periodic Access Control Policy Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.16

- `req:A.5.16:identity_register` (register) — Identity Register
- `req:A.5.16:identity_program_review` (review_record) — Periodic Identity-Management Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.16:identity_revocation_record` (revocation_record) — Per-Identity Revocation Record

### A.5.17

- `req:A.5.17:credential_register` (register) — Credential Register
- `req:A.5.17:authentication_program_review` (review_record) — Periodic Authentication-Information Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.17:credential_revocation_record` (revocation_record) — Per-Credential Revocation / Reissue Record

### A.5.18

- `req:A.5.18:access_rights_register` (register) — Access Rights Register  ✅ done → `access_register_pii.yaml`
- `req:A.5.18:access_rights_review` (review_record) — Periodic Access Rights Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.18:access_revocation_record` (revocation_record) — Access Revocation Records

### A.5.19

- `req:A.5.19:supplier_register` (register) — Supplier Register
- `req:A.5.19:portfolio_review` (review_record) — Periodic Supplier Portfolio Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.19:offboarding_record` (revocation_record) — Supplier Offboarding Records

### A.5.20

- `req:A.5.20:coverage_register` (register) — Supplier Agreement Coverage Register
- `req:A.5.20:template_review` (review_record) — Periodic Supplier Agreement Template Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.20:deviation_register` (revocation_record) — Supplier Agreement Deviation Register

### A.5.21

- `req:A.5.21:ict_component_register` (register) — ICT Component / Vendor Register
- `req:A.5.21:supply_chain_review` (review_record) — Periodic ICT Supply Chain Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.21:eol_replacement_record` (revocation_record) — ICT Component End-of-Life Replacement Records

### A.5.22

- `req:A.5.22:supplier_review_record` (review_record) — Supplier Information Security Review Records  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.22:review_schedule_register` (register) — Supplier Review Schedule Register
- `req:A.5.22:program_meta_review` (review_record) — Periodic Supplier Review Program Meta-Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.22:change_response_log` (revocation_record) — Supplier Service Change Response Log

### A.5.23

- `req:A.5.23:cloud_service_register` (register) — Cloud Service Register
- `req:A.5.23:cloud_posture_review` (review_record) — Periodic Cloud Service Posture Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.23:exit_migration_record` (revocation_record) — Cloud Service Exit / Migration Records

### A.5.24

- `req:A.5.24:incident_response_team_register` (register) — Incident Response Team Register
- `req:A.5.24:framework_program_review` (review_record) — Periodic Incident Management Framework Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.24:framework_exercise_record` (revocation_record) — Per-Exercise Framework Activation Record

### A.5.25

- `req:A.5.25:event_triage_log` (register) — Security Event Triage Log
- `req:A.5.25:triage_program_review` (review_record) — Periodic Event Triage Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.25:triage_decision_record` (revocation_record) — Per-Event Triage Decision Records

### A.5.26

- `req:A.5.26:incident_register` (register) — Information Security Incident Register  ✅ done → `incident_log.yaml`
- `req:A.5.26:ir_program_review` (review_record) — Periodic Incident Response Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.26:incident_closure_record` (revocation_record) — Per-Incident Closure Records

### A.5.27

- `req:A.5.27:lessons_register` (register) — Lessons Learned Register
- `req:A.5.27:lessons_program_review` (review_record) — Periodic Lessons-Learned Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.27:improvement_action_record` (revocation_record) — Per-Lesson Improvement Action Records

### A.5.28

- `req:A.5.28:evidence_custody_register` (register) — Evidence Custody Register
- `req:A.5.28:evidence_program_review` (review_record) — Periodic Evidence-Handling Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.28:evidence_disposal_record` (revocation_record) — Per-Package Evidence Disposal / Handover Record

### A.5.29

- `req:A.5.29:disruption_scenario_register` (register) — Disruption Scenario Register
- `req:A.5.29:continuity_program_review` (review_record) — Periodic Continuity-Security Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.29:plan_activation_record` (revocation_record) — Per-Activation Plan Record

### A.5.30

- `req:A.5.30:ict_service_register` (register) — ICT Service Continuity Register
- `req:A.5.30:ict_program_review` (review_record) — Periodic ICT Readiness Program Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.30:ict_recovery_record` (revocation_record) — Per-Recovery Event Record

### A.5.31

- `req:A.5.31:legal_regulatory_register` (register) — Legal, Statutory, Regulatory and Contractual Requirements Register
- `req:A.5.31:obligations_register_review` (review_record) — Periodic Legal/Regulatory Register Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.32

- `req:A.5.32:licensed_software_ipr_inventory` (register) — Licensed Software and IPR Inventory
- `req:A.5.32:ipr_audit_review` (review_record) — Periodic IPR and Licence Audit  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.33

- `req:A.5.33:records_schedule_register` (register) — Records Schedule (Per-Class Retention and Protection Register)
- `req:A.5.33:records_program_review` (review_record) — Periodic Records Protection Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.34

- `req:A.5.34:pii_processing_register` (register) — PII Processing Register
- `req:A.5.34:privacy_program_review` (review_record) — Periodic Privacy and PII Protection Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.5.35

- `req:A.5.35:review_schedule_register` (register) — Independent Review Schedule Register
- `req:A.5.35:review_program_meta_review` (review_record) — Periodic Independent Review Program Meta-Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.35:finding_response_register` (revocation_record) — Independent Review Finding Response Register

### A.5.36

- `req:A.5.36:compliance_review_record` (review_record) — Compliance Review Records (Policies, Rules, Standards)  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.36:compliance_review_schedule` (register) — Compliance Review Schedule
- `req:A.5.36:compliance_program_meta_review` (review_record) — Periodic Compliance Review Program Meta-Review  ⚠️ borderline (review_record — register-style or minutes?)
- `req:A.5.36:nonconformity_register` (revocation_record) — Compliance Nonconformity Register

### A.5.37

- `req:A.5.37:operating_procedures_register` (register) — Documented Operating Procedures Register
- `req:A.5.37:procedures_program_review` (review_record) — Periodic Operating Procedures Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.6.1

- `req:A.6.1:screening_record_register` (register) — Per-Candidate Screening Record Register
- `req:A.6.1:screening_program_review` (review_record) — Periodic Screening Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.6.2

- `req:A.6.2:signed_terms_register` (register) — Signed Employment Terms Register
- `req:A.6.2:terms_template_review` (review_record) — Periodic Employment Terms Template Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.6.3

- `req:A.6.3:training_completion_register` (register) — Training Completion Register
- `req:A.6.3:awareness_programme_review` (review_record) — Periodic Awareness Programme Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.6.4

- `req:A.6.4:disciplinary_case_register` (register) — Disciplinary Case Register
- `req:A.6.4:disciplinary_process_review` (review_record) — Periodic Disciplinary Process Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.6.5

- `req:A.6.5:leaver_briefing_register` (register) — Leaver Briefing Register
- `req:A.6.5:post_employment_program_review` (review_record) — Periodic Post-Employment Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.6.6

- `req:A.6.6:nda_signature_register` (register) — NDA Signature Register
- `req:A.6.6:nda_template_review` (review_record) — Periodic NDA Template Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.6.8

- `req:A.6.8:event_report_register` (register) — Event Report Register
- `req:A.6.8:reporting_program_review` (review_record) — Periodic Reporting Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.1

- `req:A.7.1:perimeter_register` (register) — Per-Site Perimeter Register
- `req:A.7.1:perimeter_program_review` (review_record) — Periodic Perimeter Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.2

- `req:A.7.2:entry_event_register` (register) — Physical Entry Event Register
- `req:A.7.2:entry_program_review` (review_record) — Periodic Entry Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.3

- `req:A.7.3:room_register` (register) — Room Register
- `req:A.7.3:rooms_program_review` (review_record) — Periodic Rooms Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.4

- `req:A.7.4:monitoring_event_register` (register) — Monitoring Event Register
- `req:A.7.4:monitoring_program_review` (review_record) — Periodic Monitoring Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.5

- `req:A.7.5:threat_register` (register) — Per-Site Threat Register
- `req:A.7.5:environmental_program_review` (review_record) — Periodic Environmental Protection Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.6

- `req:A.7.6:work_session_register` (register) — Secure Area Work Session Register
- `req:A.7.6:secure_work_program_review` (review_record) — Periodic Secure Work Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.7

- `req:A.7.7:cd_cs_audit_register` (register) — Clear Desk / Clear Screen Audit Register
- `req:A.7.7:cd_cs_program_review` (review_record) — Periodic Clear Desk / Clear Screen Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.8

- `req:A.7.8:siting_register` (register) — Equipment Siting Register
- `req:A.7.8:siting_program_review` (review_record) — Periodic Equipment Siting Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.9

- `req:A.7.9:off_premises_register` (register) — Off-Premises Asset Register
- `req:A.7.9:off_premises_program_review` (review_record) — Periodic Off-Premises Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.10

- `req:A.7.10:media_register` (register) — Storage Media Register
- `req:A.7.10:media_program_review` (review_record) — Periodic Storage Media Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.11

- `req:A.7.11:utility_register` (register) — Per-Site Utility Register
- `req:A.7.11:utilities_program_review` (review_record) — Periodic Utilities Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.12

- `req:A.7.12:cabling_register` (register) — Cabling Run Register
- `req:A.7.12:cabling_program_review` (review_record) — Periodic Cabling Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.13

- `req:A.7.13:maintenance_event_register` (register) — Maintenance Event Register
- `req:A.7.13:maintenance_program_review` (review_record) — Periodic Maintenance Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.7.14

- `req:A.7.14:disposal_record` (revocation_record) — Per-Equipment Disposal Record
- `req:A.7.14:disposal_program_review` (review_record) — Periodic Disposal Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.1

- `req:A.8.1:endpoint_register` (register) — Endpoint Inventory Register
- `req:A.8.1:endpoint_program_review` (review_record) — Periodic Endpoint Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.2

- `req:A.8.2:privileged_activity_log` (monitoring_record) — Privileged Activity Log
- `req:A.8.2:privileged_access_recertification` (review_record) — Privileged Access Recertification  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.3

- `req:A.8.3:access_matrix_register` (register) — Per-System Access Matrix Register
- `req:A.8.3:access_restriction_program_review` (review_record) — Periodic Access Restriction Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.4

- `req:A.8.4:source_code_monitoring_log` (monitoring_record) — Source Code Access Monitoring Log
- `req:A.8.4:source_code_review` (review_record) — Periodic Source Code Access Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.5

- `req:A.8.5:authentication_log` (monitoring_record) — Authentication Activity Log
- `req:A.8.5:authentication_program_review` (review_record) — Periodic Authentication Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.6

- `req:A.8.6:capacity_monitoring_log` (monitoring_record) — Capacity Monitoring Log
- `req:A.8.6:capacity_program_review` (review_record) — Periodic Capacity Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.7

- `req:A.8.7:malware_coverage_register` (register) — Malware Protection Coverage Register
- `req:A.8.7:malware_program_review` (review_record) — Periodic Malware Protection Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.8

- `req:A.8.8:vulnerability_backlog_register` (register) — Vulnerability Backlog Register
- `req:A.8.8:vulnerability_program_review` (review_record) — Periodic Vulnerability Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.9

- `req:A.8.9:configuration_baseline_register` (register) — Configuration Baseline Register
- `req:A.8.9:configuration_program_review` (review_record) — Periodic Configuration Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.10

- `req:A.8.10:deletion_register` (register) — Per-Deletion Disposal Register
- `req:A.8.10:deletion_program_review` (review_record) — Periodic Deletion Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.11

- `req:A.8.11:masking_register` (register) — Per-Dataset Masking Register
- `req:A.8.11:masking_program_review` (review_record) — Periodic Masking Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.12

- `req:A.8.12:dlp_alert_log` (monitoring_record) — DLP Alert Log
- `req:A.8.12:dlp_program_review` (review_record) — Periodic DLP Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.13

- `req:A.8.13:restore_test_register` (register) — Restore Test Register
- `req:A.8.13:backup_program_review` (review_record) — Periodic Backup Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.14

- `req:A.8.14:failover_test_register` (monitoring_record) — Failover Test Register
- `req:A.8.14:redundancy_program_review` (review_record) — Periodic Redundancy Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.15

- `req:A.8.15:log_source_register` (register) — Log Source Register
- `req:A.8.15:logging_program_review` (review_record) — Periodic Logging Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.16

- `req:A.8.16:detection_register` (register) — Detection Use-Case Register
- `req:A.8.16:monitoring_program_review` (review_record) — Periodic Monitoring Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.17

- `req:A.8.17:sync_register` (register) — Clock Sync Status Register
- `req:A.8.17:sync_program_review` (review_record) — Periodic Clock Sync Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.18

- `req:A.8.18:utility_register` (register) — Privileged Utility Programs Register
- `req:A.8.18:utility_program_review` (review_record) — Periodic Privileged Utility Programs Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.19

- `req:A.8.19:installation_register` (register) — Software Installation Register
- `req:A.8.19:installation_program_review` (review_record) — Periodic Installation Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.20

- `req:A.8.20:network_register` (register) — Network Inventory Register
- `req:A.8.20:network_program_review` (review_record) — Periodic Network Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.21

- `req:A.8.21:service_register` (register) — Network Services Register
- `req:A.8.21:service_program_review` (review_record) — Periodic Network Services Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.22

- `req:A.8.22:zone_register` (register) — Network Zone Register
- `req:A.8.22:segregation_program_review` (review_record) — Periodic Network Segregation Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.23

- `req:A.8.23:filtering_event_register` (register) — Web Filtering Event Register
- `req:A.8.23:filtering_program_review` (review_record) — Periodic Web Filtering Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.24

- `req:A.8.24:key_register` (register) — Cryptographic Key Register
- `req:A.8.24:crypto_program_review` (review_record) — Periodic Cryptography Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.25

- `req:A.8.25:project_register` (register) — Development Project Register
- `req:A.8.25:sdlc_program_review` (review_record) — Periodic SDLC Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.26

- `req:A.8.26:application_register` (register) — Application Security Requirements Register
- `req:A.8.26:appsec_program_review` (review_record) — Periodic Application Security Requirements Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.27

- `req:A.8.27:architecture_register` (register) — Reference Architecture Register
- `req:A.8.27:architecture_program_review` (review_record) — Periodic Architecture Principles Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.28

- `req:A.8.28:finding_register` (register) — Secure Coding Finding Register
- `req:A.8.28:coding_program_review` (review_record) — Periodic Secure Coding Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.29

- `req:A.8.29:test_register` (register) — Security Test Register
- `req:A.8.29:test_program_review` (review_record) — Periodic Security Testing Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.30

- `req:A.8.30:engagement_register` (register) — Outsourced Development Engagement Register
- `req:A.8.30:outsourced_program_review` (review_record) — Periodic Outsourced Development Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.31

- `req:A.8.31:environment_register` (register) — Environment Register
- `req:A.8.31:environment_program_review` (review_record) — Periodic Environment Separation Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.32

- `req:A.8.32:change_register` (register) — Change Register
- `req:A.8.32:change_program_review` (review_record) — Periodic Change Management Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.33

- `req:A.8.33:test_dataset_register` (register) — Test Dataset Register
- `req:A.8.33:test_data_program_review` (review_record) — Periodic Test Information Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### A.8.34

- `req:A.8.34:audit_engagement_register` (register) — Audit Testing Engagement Register
- `req:A.8.34:audit_testing_program_review` (review_record) — Periodic Audit Testing Protection Program Review  ⚠️ borderline (review_record — register-style or minutes?)

## GDPR:2016/679

### Art.6

- `req:Art.6:lawful_basis_register` (lawful_basis_register) — Lawful Basis Register (Art.6)
- `req:Art.6:lawful_basis_program_review` (review_record) — Lawful Basis Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.7

- `req:Art.7:consent_register` (register) — Consent Register
- `req:Art.7:consent_program_review` (review_record) — Consent Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.8

- `req:Art.8:child_consent_register` (register) — Child Consent Register
- `req:Art.8:child_consent_program_review` (review_record) — Child Consent Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.9

- `req:Art.9:special_category_processing_register` (register) — Special Category Processing Register
- `req:Art.9:special_category_program_review` (review_record) — Special Category Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.10

- `req:Art.10:criminal_data_processing_register` (register) — Criminal Data Processing Register
- `req:Art.10:criminal_data_program_review` (review_record) — Criminal Data Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.12

- `req:Art.12:rights_request_register` (register) — Rights Request Register
- `req:Art.12:transparency_program_review` (review_record) — Transparency Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.13

- `req:Art.13:publication_record` (publication_record) — Privacy Notice Publication Record
- `req:Art.13:privacy_notice_program_review` (review_record) — Privacy Notice Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.14

- `req:Art.14:source_register` (register) — Art.14 Source Register
- `req:Art.14:privacy_notice_program_review` (review_record) — Art.14 Privacy Notice Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.15

- `req:Art.15:dsar_register` (register) — DSAR Register
- `req:Art.15:dsar_process_review` (review_record) — Periodic DSAR Process Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.16

- `req:Art.16:rectification_register` (register) — Rectification Request Register
- `req:Art.16:program_review` (review_record) — Art.16 Rectification Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.17

- `req:Art.17:erasure_register` (register) — Erasure Request Register
- `req:Art.17:program_review` (review_record) — Art.17 Erasure Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.18

- `req:Art.18:restriction_register` (register) — Restriction Register
- `req:Art.18:restriction_program_review` (review_record) — Restriction Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.19

- `req:Art.19:notification_register` (register) — Recipient Notification Register
- `req:Art.19:notification_program_review` (review_record) — Art.19 Notification Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.20

- `req:Art.20:portability_register` (register) — Portability Request Register
- `req:Art.20:portability_program_review` (review_record) — Portability Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.21

- `req:Art.21:objection_register` (register) — Objection Register
- `req:Art.21:objection_program_review` (review_record) — Objection Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.22

- `req:Art.22:automated_decision_register` (register) — Automated Decision-Making Register
- `req:Art.22:automated_decision_program_review` (review_record) — Automated Decision-Making Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.23

- `req:Art.23:restriction_register` (register) — Art.23 Restriction Application Register
- `req:Art.23:restrictions_program_review` (review_record) — Art.23 Restrictions Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.24

- `req:Art.24:gdpr_compliance_register` (register) — GDPR Compliance Register
- `req:Art.24:controller_processor_decision_record` (decision_record) — Controller / Processor Role Decision Record
- `req:Art.24:accountability_program_review` (review_record) — Accountability Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.25

- `req:Art.25:default_settings_record` (configuration_record) — Privacy-default configuration record (Art.25.2)
- `req:Art.25:program_review` (review_record) — DPbD Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.26

- `req:Art.26:joint_controller_register` (register) — Joint Controller Register
- `req:Art.26:joint_controller_program_review` (review_record) — Joint Controller Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.27

- `req:Art.27:representative_operations_record` (register) — Representative Operations Record
- `req:Art.27:representative_program_review` (review_record) — Representative Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.28

- `req:Art.28:processor_register` (register) — Per-Processor DPA Register
- `req:Art.28:processor_program_review` (review_record) — Processor Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.29

- `req:Art.29:personnel_authorisation_register` (register) — Personnel Authorisation Register
- `req:Art.29:processing_under_authority_program_review` (review_record) — Processing Under Authority Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.30

- `req:Art.30:records_of_processing` (records_of_processing) — Records of Processing Activities (RoPA)
- `req:Art.30:data_flow_inventory` (data_flow_inventory) — Personal Data Flow Inventory
- `req:Art.30:ropa_annual_review` (review_record) — RoPA Periodic Review Record  ⚠️ borderline (review_record — register-style or minutes?)

### Art.31

- `req:Art.31:interaction_register` (register) — SA Interaction Register
- `req:Art.31:cooperation_program_review` (review_record) — SA Cooperation Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.32

- `req:Art.32:resilience_test` (test_log) — Periodic resilience and restoration test record
- `req:Art.32:risk_appropriate_measures_register` (register) — Risk-Appropriate Measures Register (Art.32.1)
- `req:Art.32:program_review` (review_record) — Art.32 Security Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.33

- `req:Art.33:breach_program_review` (review_record) — Breach Notification Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.34

- `req:Art.34:subject_communication_record` (register) — Subject Communication Record
- `req:Art.34:subject_communication_program_review` (review_record) — Art.34 Subject Communication Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.35

- `req:Art.35:dpia_register` (register) — DPIA Register
- `req:Art.35:dpia_program_review` (review_record) — DPIA Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.36

- `req:Art.36:consultation_register` (register) — Prior Consultation Register
- `req:Art.36:consultation_program_review` (review_record) — Art.36 Prior Consultation Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.37

- `req:Art.37:designation_record` (register) — DPO Designation Record
- `req:Art.37:dpo_designation_program_review` (review_record) — DPO Designation Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.38

- `req:Art.38:position_evidence_register` (register) — DPO Position Evidence Register
- `req:Art.38:position_program_review` (review_record) — DPO Position Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.39

- `req:Art.39:dpo_activity_register` (register) — DPO Activity Register
- `req:Art.39:dpo_tasks_program_review` (review_record) — DPO Tasks Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.40

- `req:Art.40:adherence_register` (register) — Code Adherence Register
- `req:Art.40:code_program_review` (review_record) — Code Adherence Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.41

- `req:Art.41:monitoring_record` (register) — Code Monitoring Activity Record
- `req:Art.41:monitoring_program_review` (review_record) — Code Monitoring Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.42

- `req:Art.42:certification_register` (register) — Certification Register
- `req:Art.42:certification_program_review` (review_record) — Certification Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.43

- `req:Art.43:certification_issuance_record` (register) — Certification Issuance Record
- `req:Art.43:cert_body_program_review` (review_record) — Cert Body Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.44

- `req:Art.44:transfer_register` (register) — International Transfer Register
- `req:Art.44:transfer_program_review` (review_record) — Transfer Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.45

- `req:Art.45:adequacy_register` (register) — Adequacy Reliance Register
- `req:Art.45:adequacy_program_review` (review_record) — Adequacy Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.46

- `req:Art.46:safeguards_register` (register) — Safeguards Register
- `req:Art.46:safeguards_program_review` (review_record) — Safeguards Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.47

- `req:Art.47:bcr_register` (register) — BCR Coverage Register
- `req:Art.47:bcr_program_review` (review_record) — BCR Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.48

- `req:Art.48:foreign_request_register` (register) — Foreign Authority Request Register
- `req:Art.48:foreign_authority_program_review` (review_record) — Foreign Authority Program Review  ⚠️ borderline (review_record — register-style or minutes?)

### Art.49

- `req:Art.49:invocation_register` (register) — Derogation Invocation Register
- `req:Art.49:derogations_program_review` (review_record) — Derogations Program Review  ⚠️ borderline (review_record — register-style or minutes?)
