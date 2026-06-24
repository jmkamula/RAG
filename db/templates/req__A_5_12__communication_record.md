---
leaf_id: req:A.5.12:communication_record
control_ref: A.5.12
standard_id: ISO27001:2022
evidence_type: communication_record
trigger_type: universal
template_version: 1
must_count: 5
should_count: 2
---

# Classification Scheme Communication Record

> Every information creator (i.e. every employee) needs to know which level applies and how to classify their output — an unknown scheme produces unclassified information by default, which collapses A.5.13 and A.5.10 downstream. Evidence must show active distribution and ideally individual training completion

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Date of publication/communication

<<MUST item:A.5.12:comm_date>>
_Why: Operational sufficiency_

<<TEXT>>

## 2. Audience reached (all information creators, owners, custodians — broader than just data owners)

<<MUST item:A.5.12:comm_audience>>
_Why: 27002:5.12 — all relevant personnel_

<<TEXT>>

## 3. Channel used (mandatory training module, classification guide, role-specific workshops)

<<MUST item:A.5.12:comm_channel>>
_Why: Operational sufficiency_

<<TEXT>>

## 4. Classification training completion captured at user level (proves users can apply the scheme)

<<MUST item:A.5.12:comm_training>>
_Why: Operational fitness_

<<TEXT>>

## 5. Distribution at onboarding for new personnel evidenced (induction pack, mandatory module)

<<MUST item:A.5.12:comm_onboarding>>
_Why: 27002:5.12 — new joiners_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Periodic refresher referenced (annual at minimum, especially after scheme amendments)

<<SHOULD item:A.5.12:comm_refresh>>
_Why: Sustained communication_

<<TEXT>>

### 2. Practical aids referenced (decision tree, sensitivity-label automation, examples library)

<<SHOULD item:A.5.12:comm_practical_aids>>
_Why: Adoption_

<<TEXT>>
