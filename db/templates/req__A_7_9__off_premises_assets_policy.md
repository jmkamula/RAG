---
leaf_id: req:A.7.9:off_premises_assets_policy
control_ref: A.7.9
standard_id: ISO27001:2022
evidence_type: policy
trigger_type: universal
template_version: 1
must_count: 6
should_count: 2
---

# Security of Assets Off-Premises Policy

> A.7.9 requires off-site assets to be protected. The policy documents scope, encryption, theft/loss reporting, travel restrictions, registration, return. The off-premises asset register, applicable-classes scope and periodic review are sibling leaves

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Scope (laptops, mobile devices, removable media, equipment taken off-premises)

<<MUST item:A.7.9:scope>>
_Why: 27002:7.9 — off-site assets_

<<TEXT>>

## 2. Encryption requirements for off-premises information storage

<<MUST item:A.7.9:encryption>>
_Why: 27002:7.9 — protected_

<<TEXT>>

## 3. Theft/loss reporting requirement with timeline (cross-link to A.6.8 event reporting)

<<MUST item:A.7.9:theft_loss_report>>
_Why: 27002:7.9 — protected_

<<TEXT>>

## 4. Travel restrictions or extra precautions for high-risk jurisdictions (border-crossing data minimisation)

<<MUST item:A.7.9:travel_restrictions>>
_Why: 27002:7.9 — protected_

<<TEXT>>

## 5. Registration / sign-out of equipment before removal from premises

<<MUST item:A.7.9:registration>>
_Why: 27002:7.9 — off-site assets_

<<TEXT>>

## 6. Return procedures and post-return inspection (tamper-check, integrity verification)

<<MUST item:A.7.9:return_procedures>>
_Why: 27002:7.9 — protected_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Reference to remote working policy (A.6.7) where home is the off-premises location

<<SHOULD item:A.7.9:home_office_link>>
_Why: Cross-control consistency_

<<TEXT>>

### 2. Specific guidance for conferences and customer-site visits (loaner devices, data minimisation)

<<SHOULD item:A.7.9:conference_travel>>
_Why: Common operational case_

<<TEXT>>
