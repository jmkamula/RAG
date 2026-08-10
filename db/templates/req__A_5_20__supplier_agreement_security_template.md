---
leaf_id: req:A.5.20:supplier_agreement_security_template
control_ref: A.5.20
standard_id: ISO27001:2022
evidence_type: agreement_template
trigger_type: universal
template_version: 1
must_count: 14
should_count: 2
---

# Supplier Agreement Security Requirements Template

<<DOC_CONTROL>>

> A.5.20 requires information security requirements to be established and agreed with each supplier based on the relationship type. The template is the standard clause set attached to supplier agreements; the coverage register, periodic template review and deviation register are sibling leaves

## What this template gives you

This template provides a ready-to-use set of security requirements clauses for supplier agreements, helping you ensure your contracts meet ISO 27001 expectations for managing supplier relationships.

## When to use it

Use this template whenever you are drafting or updating agreements with suppliers, and review or refresh it as your supplier relationships or security needs change.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 2.5 to 3.5 hours completing this template from scratch, as each required element takes around 10-15 minutes to fill in thoughtfully.

## 1. Minimum security requirements (controls baseline, certifications expected)

<<MUST item:A.5.20:minimum_requirements>>
_Why: 27002:5.20a,g_

<<GUIDANCE>>

<<TEXT>>

## 2. Information classification mapping (org scheme → supplier scheme where they differ)

<<MUST item:A.5.20:classification_map>>
_Why: 27002:5.20b_

<<GUIDANCE>>

<<TEXT>>

## 3. Legal, statutory, regulatory, contractual obligations (data protection, IP, copyright)

<<MUST item:A.5.20:legal_compliance>>
_Why: 27002:5.20c,p_

<<GUIDANCE>>

<<TEXT>>

## 4. Data handling requirements (encryption at rest and in transit, location/sovereignty)

<<MUST item:A.5.20:data_handling>>
_Why: 27002:5.20a — security requirements_

<<GUIDANCE>>

<<TEXT>>

## 5. Acceptable + unacceptable use rules stated

<<MUST item:A.5.20:acceptable_use>>
_Why: 27002:5.20e_

<<GUIDANCE>>

<<TEXT>>

## 6. Named or role-defined authorized personnel + conditions for access

<<MUST item:A.5.20:authorized_personnel>>
_Why: 27002:5.20f_

<<GUIDANCE>>

<<TEXT>>

## 7. Incident notification clause with timeline (e.g. within 24h of detection) + collaboration during remediation

<<MUST item:A.5.20:incident_notification>>
_Why: 27002:5.20h_

<<GUIDANCE>>

<<TEXT>>

## 8. Training and awareness requirements specific to information and access

<<MUST item:A.5.20:training_awareness>>
_Why: 27002:5.20i_

<<GUIDANCE>>

<<TEXT>>

## 9. Sub-processor / fourth-party restrictions, approval process and propagation of requirements

<<MUST item:A.5.20:subprocessor_limits>>
_Why: 27002:5.20j_

<<GUIDANCE>>

<<TEXT>>

## 10. Security incident contacts named on each side

<<MUST item:A.5.20:incident_contacts>>
_Why: 27002:5.20k_

<<GUIDANCE>>

<<TEXT>>

## 11. Screening / vetting requirements for supplier personnel (where applicable)

<<MUST item:A.5.20:screening>>
_Why: 27002:5.20l_

<<GUIDANCE>>

<<TEXT>>

## 12. Audit rights (right to audit; accept attestations like ISO 27001 / SOC 2 in lieu)

<<MUST item:A.5.20:audit_rights>>
_Why: 27002:5.20m,o_

<<GUIDANCE>>

<<TEXT>>

## 13. Defect resolution and conflict resolution processes

<<MUST item:A.5.20:defect_resolution>>
_Why: 27002:5.20n_

<<GUIDANCE>>

<<TEXT>>

## 14. Termination obligations: data return/destruction, transition arrangements, handover of records

<<MUST item:A.5.20:termination_return>>
_Why: 27002:5.20q,r_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Security-specific SLAs (e.g. patching cadence, MFA requirements, vulnerability remediation timelines)

<<SHOULD item:A.5.20:security_sla>>
_Why: Measurable accountability_

<<GUIDANCE>>

<<TEXT>>

### 2. Variant clause sets per supplier tier

<<SHOULD item:A.5.20:tier_variants>>
_Why: Proportionality_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
