---
leaf_id: req:A.5.34:privacy_and_pii_protection_policy
control_ref: A.5.34
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 8
should_count: 4
---

# Privacy and PII Protection Policy

> A.5.34 requires identification of and compliance with privacy and PII protection requirements per applicable law, regulation, and contract. The policy (PIMS-aligned where ISO/IEC 27701 is in scope) names the applicable privacy laws, states the lawful basis discipline, enables data subject rights, sets retention/minimisation, links to the operational security controls applied to PII, and documents breach handling. The PII processing register, privacy applicability scope and periodic program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Applicable privacy laws identified (GDPR, UK GDPR, regional equivalents, sectoral privacy laws — HIPAA, LGPD, PIPEDA, CCPA, etc.) — each named, not just 'privacy laws'

<<MUST item:A.5.34:applicable_laws>>
_Why: 27002:5.34 — applicable laws and regulations_

<<TEXT>>

## 2. Lawful basis discipline (lawful basis identified per processing activity — consent, contract, legal obligation, vital interests, public task, legitimate interests; where law requires)

<<MUST item:A.5.34:lawful_basis>>
_Why: 27002:5.34 — applicable laws / GDPR Art.6_

<<TEXT>>

## 3. Data subject rights enabled (access, rectification, erasure, portability, restriction, objection where applicable; intake path + response SLAs documented — cross-link to GDPR Art.12-22 and DSAR procedure)

<<MUST item:A.5.34:data_subject_rights>>
_Why: 27002:5.34 — preservation of privacy_

<<TEXT>>

## 4. Retention and data minimisation requirements (collect only what's necessary; retain only as long as needed; cross-link to A.5.33 records schedule and GDPR Art.5.1.c/e)

<<MUST item:A.5.34:retention_minimisation>>
_Why: 27002:5.34 — preservation of privacy / GDPR Art.5.1.c+e_

<<TEXT>>

## 5. References security controls applied to PII (links to A.8.x technical controls — encryption A.8.24, access control A.5.15/A.8.3, logging A.8.15/A.8.16, pseudonymisation A.8.11; satisfies GDPR Art.32 integration with Art.5.1.f)

<<MUST item:A.5.34:security_controls_ref>>
_Why: 27002:5.34 — protection of PII / GDPR Art.32_

<<TEXT>>

## 6. Breach handling reference (cross-link to A.5.24/A.5.26 incident family + GDPR Art.33 supervisory-authority notification within 72h + GDPR Art.34 data-subject notification where high risk)

<<MUST item:A.5.34:breach_handling>>
_Why: 27002:5.34 — applicable laws / GDPR Art.33-34_

<<TEXT>>

## 7. Cross-border transfer discipline (which transfers happen, on what legal basis — SCCs / adequacy / BCRs / derogations; cross-link to A.5.14 transfer policy + GDPR Art.44-49)

<<MUST item:A.5.34:transfer_restrictions>>
_Why: 27002:5.34 — preservation of privacy / GDPR Chap V_

<<TEXT>>

## 8. Named owner of the privacy program (DPO where law requires; Privacy Officer or InfoSec lead where DPO is not mandatory; named individual, not a generic 'Privacy Team')

<<MUST item:A.5.34:owner>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. PIA / DPIA process reference for high-risk processing (cross-link to GDPR Art.35 + EDPB Guidelines on DPIA — when to trigger, who reviews, supervisory-authority consultation path)

<<SHOULD item:A.5.34:dpia_process>>
_Why: Pre-emptive risk handling_

<<TEXT>>

### 2. DPO designation note (mandatory under GDPR Art.37 for public authorities, large-scale special-category processing, large-scale systematic monitoring; voluntary otherwise — captured here regardless of mandate)

<<SHOULD item:A.5.34:dpo_role>>
_Why: Accountability_

<<TEXT>>

### 3. Cross-link to A.6.3 awareness — privacy/PII training for staff who process personal data (consent capture, DSAR handling, breach reporting)

<<SHOULD item:A.5.34:training_link>>
_Why: Effectiveness_

<<TEXT>>

### 4. ISO/IEC 27701 (PIMS) alignment note where applicable — extends the ISMS into a Privacy Information Management System; references the 27701 PII-controller / PII-processor controls applied

<<SHOULD item:A.5.34:pims_alignment>>
_Why: 27701 integration where in scope_

<<TEXT>>
