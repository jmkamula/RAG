---
leaf_id: req:A.5.15:access_control_policy
control_ref: A.5.15
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 7
should_count: 3
---

# Access Control Policy

> A.5.15 requires rules controlling physical and logical access based on business and information security requirements. The policy states the principles and decision rules; the provisioning procedure (lifecycle) lives at A.5.18. Approval, communication and periodic review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Physical access rules (premises, server rooms, restricted areas)

<<MUST item:A.5.15:physical_rules>>
_Why: 27002:5.15 — physical access_

<<TEXT>>

## 2. Logical access rules (systems, applications, network segments)

<<MUST item:A.5.15:logical_rules>>
_Why: 27002:5.15 — logical access_

<<TEXT>>

## 3. Role-based access control as the default model with stated exceptions (attribute-based, individual grants)

<<MUST item:A.5.15:rbac>>
_Why: 27002:5.15 — business requirements_

<<TEXT>>

## 4. Principle of least privilege stated

<<MUST item:A.5.15:least_privilege>>
_Why: 27002:5.15 — security requirements_

<<TEXT>>

## 5. Principle of need-to-know stated

<<MUST item:A.5.15:need_to_know>>
_Why: 27002:5.15 — security requirements_

<<TEXT>>

## 6. Authorisation rules — who can authorise access at which level (cross-link to A.5.18 procedure)

<<MUST item:A.5.15:authorisation>>
_Why: 27002:5.15 — established_

<<TEXT>>

## 7. Cross-link to A.5.3 segregation of duties — access decisions respect documented separation

<<MUST item:A.5.15:segregation_link>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Emergency / break-glass access provisions (with mandatory after-the-fact justification)

<<SHOULD item:A.5.15:emergency_access>>
_Why: Operational continuity_

<<TEXT>>

### 2. Third-party / contractor access rules referenced (link to A.5.19 supplier relationships)

<<SHOULD item:A.5.15:third_party>>
_Why: Coverage_

<<TEXT>>

### 3. Periodic access review cadence stated (typically quarterly for privileged, annual otherwise — link to A.5.18)

<<SHOULD item:A.5.15:review_cadence>>
_Why: Drift prevention_

<<TEXT>>
