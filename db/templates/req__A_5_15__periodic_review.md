---
leaf_id: req:A.5.15:periodic_review
control_ref: A.5.15
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
---

# Periodic Access Control Policy Review

> Access control policies decay as the IT estate grows — new systems, new cloud services, new federated identity sources all stress the policy. Review checks whether the rules still cover the actual estate, whether least-privilege is still operationalised correctly, and whether downstream A.5.18 provisioning is aligned

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.15:review_date>>
_Why: Periodic review_

<<TEXT>>

## 2. Reviewer identity and role (typically CISO with IT and identity-management input)

<<MUST item:A.5.15:review_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Outcome captured (no change / amended / re-issued) with rationale per amendment

<<MUST item:A.5.15:review_outcome>>
_Why: Periodic review_

<<TEXT>>

## 4. Estate-alignment check — new systems / cloud services added since last review reflected in policy

<<MUST item:A.5.15:review_estate>>
_Why: Drift catch_

<<TEXT>>

## 5. A.5.18 provisioning procedure cross-checked for alignment with policy changes

<<MUST item:A.5.15:review_a518_link>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc triggers listed (M&A, new identity provider, major SaaS adoption, access-related incident)

<<SHOULD item:A.5.15:review_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.15:review_next_date>>
_Why: Planning_

<<TEXT>>
