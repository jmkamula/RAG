---
leaf_id: req:A.7.2:entry_program_review
control_ref: A.7.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Entry Program Review

> Annual verification that entry controls match area classifications, the register is being maintained, and anomalies are being investigated (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.2:rev_date>>
_Why: 27002:7.2 — periodic_

<<TEXT>>

## 2. Reviewer identity (Facilities + InfoSec)

<<MUST item:A.7.2:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-area access-list review outcome (active / amended / revoked) — cross-link to A.5.18 access review

<<MUST item:A.7.2:rev_access_lists>>
_Why: 27002:7.2 — review_

<<TEXT>>

## 4. Anomaly review (flagged events from the register triaged)

<<MUST item:A.7.2:rev_anomalies>>
_Why: Detection_

<<TEXT>>

## 5. Changes propagated to the procedure / authorisation lists

<<MUST item:A.7.2:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.2:rev_next_date>>
_Why: Planning_

<<TEXT>>
