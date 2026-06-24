---
leaf_id: req:A.8.34:audit_testing_protection_policy
control_ref: A.8.34
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 9
should_count: 1
---

# Protection of Information Systems During Audit Testing Policy

> A.8.34 requires audit/assurance activities on operational systems planned + agreed. Policy states pre-authorisation, scope-agreement requirements, time-window discipline, rollback requirement, evidence preservation, stakeholder notification. Per-engagement register, applicable scope, program review are sibling leaves

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Pre-authorisation required before any audit testing on operational systems

<<MUST item:A.8.34:pre_authorisation>>
_Why: 27002:8.34 — planned and agreed_

<<TEXT>>

## 2. Written scope-agreement required (what's in / what's out / what tests / what data)

<<MUST item:A.8.34:scope_agreement>>
_Why: 27002:8.34 — agreed_

<<TEXT>>

## 3. Time-window discipline (avoid peak business hours / change-freezes / customer events)

<<MUST item:A.8.34:time_windows>>
_Why: 27002:8.34 — planned_

<<TEXT>>

## 4. Rollback procedure stated for any change introduced during testing

<<MUST item:A.8.34:rollback>>
_Why: 27002:8.34 — protection of information systems_

<<TEXT>>

## 5. Evidence-preservation requirement (logs / results retained per legal-regulatory chain-of-custody)

<<MUST item:A.8.34:evidence_preservation>>
_Why: 27002:8.34 — assessment of operational systems_

<<TEXT>>

## 6. Stakeholder-notification requirement (affected teams / on-call / customer where material)

<<MUST item:A.8.34:stakeholder_notification>>
_Why: 27002:8.34 — agreed between the tester and management_

<<TEXT>>

## 7. Performance-impact consideration + limit

<<MUST item:A.8.34:performance_impact>>
_Why: 27002:8.34 — protection_

<<TEXT>>

## 8. Dedicated test accounts used — no re-use of real user identities (attribution clarity; Style v2 promotion)

<<MUST item:A.8.34:dedicated_accounts>>
_Why: Attribution clarity_

<<TEXT>>

## 9. Named policy authority (InfoSec lead with Internal Audit partner)

<<MUST item:A.8.34:authority>>
_Why: Accountability_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Audit-of-the-audit logs (record of testing activities for accountability of testers themselves)

<<SHOULD item:A.8.34:meta_audit>>
_Why: Accountability of testers_

<<TEXT>>
