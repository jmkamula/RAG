---
leaf_id: req:A.8.30:outsourced_program_review
control_ref: A.8.30
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# Periodic Outsourced Development Program Review

> Annual verification — engagement-register currency, delivered-code-test coverage, vendor incident patterns (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.30:rev_date>>
_Why: 27002:8.30 — periodic_

<<TEXT>>

## 2. Reviewer identity (Engineering + Supplier Management + InfoSec)

<<MUST item:A.8.30:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Engagement-register currency check

<<MUST item:A.8.30:rev_register_currency>>
_Why: Drift prevention_

<<TEXT>>

## 4. Delivered-code-test coverage per engagement (was every release tested before merge to production)

<<MUST item:A.8.30:rev_test_coverage>>
_Why: 27002:8.30 — review_

<<TEXT>>

## 5. Vendor incident-pattern review (cross-link to A.5.22 supplier review)

<<MUST item:A.8.30:rev_vendor_incidents>>
_Why: Cross-control coherence_

<<TEXT>>

## 6. Findings propagated to procedure / contract terms

<<MUST item:A.8.30:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.30:rev_next_date>>
_Why: Planning_

<<TEXT>>
