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

<<DOC_CONTROL>>

> A.7.9 requires off-site assets to be protected. The policy documents scope, encryption, theft/loss reporting, travel restrictions, registration, return. The off-premises asset register, applicable-classes scope and periodic review are sibling leaves

## What this template gives you

This template helps you create a clear policy for protecting company assets when they are taken off-site, including rules for encryption, reporting loss or theft, and asset registration.

## When to use it

Use this policy whenever your organization allows equipment or data to leave your main office or facility. Review and update it whenever your off-site asset practices change or as needed.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 1 to 2 hours drafting this policy from scratch, depending on the number of assets and details you need to cover.

## 1. Scope (laptops, mobile devices, removable media, equipment taken off-premises)

<<MUST item:A.7.9:scope>>
_Why: 27002:7.9 — off-site assets_

<<GUIDANCE>>

<<TEXT>>

## 2. Encryption requirements for off-premises information storage

<<MUST item:A.7.9:encryption>>
_Why: 27002:7.9 — protected_

<<GUIDANCE>>

<<TEXT>>

## 3. Theft/loss reporting requirement with timeline (cross-link to A.6.8 event reporting)

<<MUST item:A.7.9:theft_loss_report>>
_Why: 27002:7.9 — protected_

<<GUIDANCE>>

<<TEXT>>

## 4. Travel restrictions or extra precautions for high-risk jurisdictions (border-crossing data minimisation)

<<MUST item:A.7.9:travel_restrictions>>
_Why: 27002:7.9 — protected_

<<GUIDANCE>>

<<TEXT>>

## 5. Registration / sign-out of equipment before removal from premises

<<MUST item:A.7.9:registration>>
_Why: 27002:7.9 — off-site assets_

<<GUIDANCE>>

<<TEXT>>

## 6. Return procedures and post-return inspection (tamper-check, integrity verification)

<<MUST item:A.7.9:return_procedures>>
_Why: 27002:7.9 — protected_

<<GUIDANCE>>

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Reference to remote working policy (A.6.7) where home is the off-premises location

<<SHOULD item:A.7.9:home_office_link>>
_Why: Cross-control consistency_

<<GUIDANCE>>

<<TEXT>>

### 2. Specific guidance for conferences and customer-site visits (loaner devices, data minimisation)

<<SHOULD item:A.7.9:conference_travel>>
_Why: Common operational case_

<<GUIDANCE>>

<<TEXT>>

## Revision history

<<REVISION_HISTORY>>
