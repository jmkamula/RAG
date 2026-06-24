---
leaf_id: req:10.2:nc_program_review
control_ref: 10.2
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 6
should_count: 1
---

# NC/CA Program Review

> Annual verification that NCs are flowing through the procedure, root cause is being done properly (not blamed-on-individual), effectiveness checks actually prevent recurrence (freshness=365)

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:10.2:rev_date>>
_Why: Clause 10.2 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + lead auditor)

<<MUST item:10.2:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Closure-progress check — open NCs aging beyond expected closure time escalated

<<MUST item:10.2:rev_closure_progress>>
_Why: Effectiveness_

<<TEXT>>

## 4. Root-cause-quality sample — sampled NCs reviewed for blame-free systemic analysis (not 'human error' as the only cause)

<<MUST item:10.2:rev_root_cause_quality>>
_Why: Clause 10.2 b)_

<<TEXT>>

## 5. Recurrence check — closed NCs sampled for whether the same nature recurred (effectiveness failure signal)

<<MUST item:10.2:rev_recurrence_check>>
_Why: Clause 10.2 d)_

<<TEXT>>

## 6. ISMS-change pattern check — high-volume NC areas drove 6.3 ISMS changes where systemic causes warranted it

<<MUST item:10.2:rev_isms_change_pattern>>
_Why: Clause 10.2 e)_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:10.2:rev_next_date>>
_Why: Planning_

<<TEXT>>
