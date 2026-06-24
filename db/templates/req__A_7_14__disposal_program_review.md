---
leaf_id: req:A.7.14:disposal_program_review
control_ref: A.7.14
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Disposal Program Review

> Annual verification of disposal-record completeness, certificate retention, provider performance. Freshness=365

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.7.14:rev_date>>
_Why: 27002:7.14 — periodic_

<<TEXT>>

## 2. Reviewer identity (IT + InfoSec + Legal where regulatory disposal applies)

<<MUST item:A.7.14:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Completeness check — every retired asset (from A.5.9) has a matching disposal_record

<<MUST item:A.7.14:rev_completeness>>
_Why: Cross-control coherence_

<<TEXT>>

## 4. Certificate audit (sample-based verification that retained certificates match register entries)

<<MUST item:A.7.14:rev_certificate_audit>>
_Why: Auditability_

<<TEXT>>

## 5. Changes propagated to the procedure / scope

<<MUST item:A.7.14:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.7.14:rev_next_date>>
_Why: Planning_

<<TEXT>>
