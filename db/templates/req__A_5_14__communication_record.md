---
leaf_id: req:A.5.14:communication_record
control_ref: A.5.14
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Information Transfer Policy Communication Record

> Transfer-policy enforcement requires every personnel who could initiate a transfer (which is essentially everyone) to have been informed of the rules — channel choices, encryption requirements, classification gates and external-party disclosure obligations only work if people know about them. Evidence must show active distribution and ideally individual acknowledgement (signature, click-through, training completion), not mere intranet availability

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Date of publication/communication

<<MUST item:A.5.14:comm_date>>
_Why: Operational sufficiency_

<<TEXT>>

## 2. Audience reached (all in-scope users, including new joiners; targeted refresh for users who handle sensitive transfers frequently)

<<MUST item:A.5.14:comm_audience>>
_Why: 27002:5.14 — relevant personnel_

<<TEXT>>

## 3. Channel used (mandatory training module, intranet publication with notification, signature campaign)

<<MUST item:A.5.14:comm_channel>>
_Why: Operational sufficiency_

<<TEXT>>

## 4. User-level acknowledgement captured (e-signature, training completion record, click-through)

<<MUST item:A.5.14:comm_acknowledgement>>
_Why: Enforceability — burden of proof_

<<TEXT>>

## 5. Distribution at onboarding for new personnel evidenced (induction pack, mandatory module covering transfer rules + approved channels)

<<MUST item:A.5.14:comm_onboarding>>
_Why: 27002:5.14 — sustained communication_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic re-acknowledgement (annual at minimum) referenced

<<SHOULD item:A.5.14:comm_refresh>>
_Why: Sustained communication_

<<TEXT>>

### 2. Scenario-based examples included in training (e.g. external auditor data request, supplier integration handover, regulator response)

<<SHOULD item:A.5.14:comm_scenario_examples>>
_Why: Practical effectiveness_

<<TEXT>>
