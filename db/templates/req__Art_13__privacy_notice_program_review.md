---
leaf_id: req:Art.13:privacy_notice_program_review
control_ref: Art.13
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Privacy Notice Program Review

> Annual verification that the notice content is current with actual processing, the publication record reflects all deployed versions, every collection point still presents the notice (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:Art.13:rev_date>>
_Why: Art.5.2 — periodic_

<<TEXT>>

## 2. Reviewer identity (DPO or Privacy Lead)

<<MUST item:Art.13:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Content currency check — notice reflects current Art.30 RoPA + Art.6 basis register

<<MUST item:Art.13:rev_content_currency>>
_Why: Cross-article coherence_

<<TEXT>>

## 4. Coverage check — every in-scope collection point still presents the current notice

<<MUST item:Art.13:rev_collection_coverage>>
_Why: Drift detection_

<<TEXT>>

## 5. Publication archive check — prior versions retained for audit defensibility

<<MUST item:Art.13:rev_publication_archive>>
_Why: Art.5.2_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:Art.13:rev_next_date>>
_Why: Planning_

<<TEXT>>
