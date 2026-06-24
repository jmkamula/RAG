---
leaf_id: req:7.5:document_control_program_review
control_ref: 7.5
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Document Control Program Review

> Annual verification that the policy is being applied, the register is current, stale documents are surfaced and refreshed (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:7.5:rev_date>>
_Why: Clause 7.5 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + document-control lead)

<<MUST item:7.5:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Register currency check — every row reviewed; next-review dates met or rescheduled

<<MUST item:7.5:rev_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Stale-document sweep — overdue review dates surfaced; refresh or retire decisions made

<<MUST item:7.5:rev_stale_sweep>>
_Why: Drift detection_

<<TEXT>>

## 5. Coverage check — every in-scope document class has at least one register entry

<<MUST item:7.5:rev_coverage>>
_Why: Cross-leaf coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:7.5:rev_next_date>>
_Why: Planning_

<<TEXT>>
