---
leaf_id: req:A.7.9:off_premises_program_review
control_ref: A.7.9
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Off-Premises Program Review

> Annual verification that the register is current, theft/loss incidents handled, travel-restriction list still applies. Freshness=365

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.9:rev_date>>
_Why: 27002:7.9 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + InfoSec + IT lead)

<<MUST item:A.7.9:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Stale-loaner check — assets off-premises for unexpectedly long without status update

<<MUST item:A.7.9:rev_register_check>>
_Why: Operational discipline_

<<TEXT>>

## 4. Theft/loss incidents in period — handled per policy, lessons captured

<<MUST item:A.7.9:rev_incident_review>>
_Why: 27002:7.9 — protected_

<<TEXT>>

## 5. Changes propagated to the policy / scope

<<MUST item:A.7.9:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.9:rev_next_date>>
_Why: Planning_

<<TEXT>>
