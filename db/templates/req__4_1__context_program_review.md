---
leaf_id: req:4.1:context_program_review
control_ref: 4.1
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
---

# Context Program Review

> Annual verification that the issues register reflects current reality, the identification framework is being followed, and the scope still bounds the right domains (freshness=365)

> **Edit the `<<TEXT>>` placeholders inline. Leave the MUST and SHOULD markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:4.1:rev_date>>
_Why: Clause 4.1 — periodic_

<<TEXT>>

## 2. Reviewer identity (ISMS Manager + executive sponsor)

<<MUST item:4.1:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Register currency check — every row reviewed for continued relevance, new issues added

<<MUST item:4.1:rev_register_currency>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 4. Confirmation that handoff to 6.1.2 risk assessment occurred for material issues

<<MUST item:4.1:rev_risk_handoff>>
_Why: Closes the loop_

<<TEXT>>

## 5. Cross-check against the applicable-domains scope — any new domain that should be covered

<<MUST item:4.1:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Next planned review date stated

<<SHOULD item:4.1:rev_next_date>>
_Why: Planning_

<<TEXT>>
