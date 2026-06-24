---
leaf_id: req:A.5.23:cloud_services_policy
control_ref: A.5.23
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: profile_fact
template_version: 1
must_count: 12
should_count: 2
---

# Information Security for Use of Cloud Services Policy

> A.5.23 requires a topic-specific policy on use of cloud services covering scope, risk management, selection, shared-responsibility split, incident handling and exit. The cloud service register, periodic posture review and exit-migration records are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope of cloud services covered (IaaS / PaaS / SaaS, public / private / hybrid)

<<MUST item:A.5.23:scope>>
_Why: 27002:5.23a_

<<TEXT>>

## 2. How information security risks in cloud use will be managed (assessment + treatment approach)

<<MUST item:A.5.23:risk_management>>
_Why: 27002:5.23b_

<<TEXT>>

## 3. Cloud service selection criteria

<<MUST item:A.5.23:selection>>
_Why: 27002:5.23b_

<<TEXT>>

## 4. Roles and responsibilities for cloud service use and management (internal)

<<MUST item:A.5.23:responsibilities>>
_Why: 27002:5.23c_

<<TEXT>>

## 5. Shared-responsibility model: which controls are CSP-managed vs customer-managed

<<MUST item:A.5.23:shared_responsibility>>
_Why: 27002:5.23d_

<<TEXT>>

## 6. How CSP-side controls will be obtained, evaluated and used (attestation review, API checks, configuration discovery)

<<MUST item:A.5.23:controls_method>>
_Why: 27002:5.23e_

<<TEXT>>

## 7. Procedures for handling cloud-related security incidents (link to A.5.24-27, support obligations from CSP)

<<MUST item:A.5.23:incidents>>
_Why: 27002:5.23f_

<<TEXT>>

## 8. How personal data in cloud storage is protected (encryption, location/sovereignty, sub-processor controls)

<<MUST item:A.5.23:personal_data>>
_Why: GDPR Art.32 alignment_

<<TEXT>>

## 9. Cloud agreements based on accepted industry standards for architecture and infrastructure

<<MUST item:A.5.23:industry_standards>>
_Why: 27002:5.23 — agreements_

<<TEXT>>

## 10. Geographic-location requirements for sensitive data in transit and at rest

<<MUST item:A.5.23:geographic_location>>
_Why: 27002:5.23 — geo controls_

<<TEXT>>

## 11. Forensic / digital-evidence support expectations from the CSP

<<MUST item:A.5.23:forensic_support>>
_Why: 27002:5.23 — forensics_

<<TEXT>>

## 12. Sub-processing terms for cloud (CSP's own sub-processors, notification, approval)

<<MUST item:A.5.23:sub_processing>>
_Why: 27002:5.23 — sub-processing_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Malware monitoring/protection expectations stated for the cloud environment

<<SHOULD item:A.5.23:malware_protection>>
_Why: 27002:5.23 — malware_

<<TEXT>>

### 2. CSP backup of data + config and handover obligations on termination

<<SHOULD item:A.5.23:backup_handover>>
_Why: 27002:5.23 — backup_

<<TEXT>>
