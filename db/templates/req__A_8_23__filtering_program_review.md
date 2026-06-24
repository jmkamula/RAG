---
leaf_id: req:A.8.23:filtering_program_review
control_ref: A.8.23
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Web Filtering Program Review

> Annual verification — category-list currency, override-volume trending, malware-hit follow-through, coverage gaps (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.23:rev_date>>
_Why: 27002:8.23 — periodic_

<<TEXT>>

## 2. Reviewer identity (Security Operations + Legal/HR for category boundaries)

<<MUST item:A.8.23:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Category-list currency check (new malicious-content categories added; obsolete categories retired)

<<MUST item:A.8.23:rev_category_currency>>
_Why: 27002:8.23 — managed_

<<TEXT>>

## 4. Override-volume trending (spikes may indicate category over-blocking or coverage gap)

<<MUST item:A.8.23:rev_override_trending>>
_Why: Operational signal_

<<TEXT>>

## 5. Findings propagated to policy / scope

<<MUST item:A.8.23:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.23:rev_next_date>>
_Why: Planning_

<<TEXT>>
