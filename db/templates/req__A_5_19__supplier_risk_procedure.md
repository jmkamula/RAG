---
leaf_id: req:A.5.19:supplier_risk_procedure
control_ref: A.5.19
standard_id: ISO27001:2022
evidence_type: procedure
trigger_type: universal
template_version: 1
must_count: 8
should_count: 3
---

# Supplier Information Security Risk Management Procedure

> A.5.19 requires processes and procedures to manage information security risks arising from supplier relationships. The procedure documents how supplier types are identified, how selection happens, how due diligence is conducted, how monitoring is run, and how requirements get into the agreement (A.5.20). The supplier register, periodic review and offboarding records are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Supplier types identified and documented (ICT services, ICT infrastructure components, logistics, utilities, financial, etc.)

<<MUST item:A.5.19:supplier_types>>
_Why: 27002:5.19a_

<<TEXT>>

## 2. Selection and evaluation criteria based on sensitivity of information and services (risk analysis, references, attestations)

<<MUST item:A.5.19:selection_criteria>>
_Why: 27002:5.19b,c_

<<TEXT>>

## 3. InfoSec rules per supplier type / access type with minimum requirements

<<MUST item:A.5.19:risk_rules>>
_Why: 27002:5.19d,g,h_

<<TEXT>>

## 4. Due diligence steps before engagement (questionnaire, attestation review, audit)

<<MUST item:A.5.19:due_diligence>>
_Why: 27002:5.19c_

<<TEXT>>

## 5. Ongoing monitoring approach (periodic reassessment, event-triggered review, third-party reports)

<<MUST item:A.5.19:ongoing_monitoring>>
_Why: 27002:5.19e,i_

<<TEXT>>

## 6. Conditions under which security requirements get into the supplier agreement (handoff to A.5.20)

<<MUST item:A.5.19:agreement_handoff>>
_Why: 27002:5.19l_

<<TEXT>>

## 7. Training of own personnel on appropriate engagement and information exchange with suppliers

<<MUST item:A.5.19:training_personnel>>
_Why: 27002:5.19k_

<<TEXT>>

## 8. Incident and contingency handling jointly with the supplier

<<MUST item:A.5.19:incident_joint_mgmt>>
_Why: 27002:5.19n_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Tiering model with concrete criteria (data sensitivity, dependency, financial exposure)

<<SHOULD item:A.5.19:tiering_model>>
_Why: 27002:5.19b — risk-proportionate_

<<TEXT>>

### 2. Reference to standard supplier security questionnaire

<<SHOULD item:A.5.19:questionnaire_ref>>
_Why: Consistency_

<<TEXT>>

### 3. Backup or alternative supplier processes / treatment of supplier disruption

<<SHOULD item:A.5.19:resilience_plan>>
_Why: 27002:5.19j_

<<TEXT>>
