---
leaf_id: req:6.3:change_program_review
control_ref: 6.3
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# ISMS Change Program Review

> Annual verification that change identification triggers are firing, the register reflects all actual changes, the A.8.32 boundary holds (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:6.3:rev_date>>
_Why: Clause 6.3 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + change-management lead)

<<MUST item:6.3:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Register currency check — every approved change reached implementation OR was withdrawn

<<MUST item:6.3:rev_register_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Silent-change sweep — verify no scope / policy / roles changes happened without a register entry

<<MUST item:6.3:rev_silent_changes>>
_Why: Drift detection_

<<TEXT>>

## 5. A.8.32 boundary check — no technical changes mis-routed to 6.3, no ISMS changes mis-routed to A.8.32

<<MUST item:6.3:rev_boundary_check>>
_Why: Cross-control coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:6.3:rev_next_date>>
_Why: Planning_

<<TEXT>>
