---
leaf_id: req:A.8.19:installation_program_review
control_ref: A.8.19
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Periodic Installation Program Review

> Annual verification — approved-list currency, allowlist enforcement effectiveness, unauthorised-install detection trending (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.8.19:rev_date>>
_Why: 27002:8.19 — periodic_

<<TEXT>>

## 2. Reviewer identity (Infrastructure + InfoSec)

<<MUST item:A.8.19:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Approved-list currency check (no abandoned tools; vulnerable versions retired)

<<MUST item:A.8.19:rev_approved_list_currency>>
_Why: 27002:8.19 — securely manage_

<<TEXT>>

## 4. Allowlist-enforcement effectiveness review (unauthorised-install attempt rate)

<<MUST item:A.8.19:rev_allowlist_effectiveness>>
_Why: Detection effectiveness_

<<TEXT>>

## 5. Findings propagated to procedure / approved list

<<MUST item:A.8.19:rev_findings_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:A.8.19:rev_next_date>>
_Why: Planning_

<<TEXT>>
