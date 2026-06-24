---
leaf_id: req:4.4:isms_program_review
control_ref: 4.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# ISMS Manual Program Review

> Annual verification that the manual reflects current ISMS reality, the process map is current, and any changes were captured (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:4.4:rev_date>>
_Why: Clause 4.4 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + top management sponsor)

<<MUST item:4.4:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Currency check — manual still matches how the ISMS actually runs

<<MUST item:4.4:rev_currency>>
_Why: Drift detection_

<<TEXT>>

## 4. Process map currency check (cross-leaf coherence)

<<MUST item:4.4:rev_map_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Cross-check against change records — every actual change in the year is logged

<<MUST item:4.4:rev_change_log>>
_Why: Cross-leaf coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:4.4:rev_next_date>>
_Why: Planning_

<<TEXT>>
