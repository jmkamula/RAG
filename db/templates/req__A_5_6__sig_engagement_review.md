---
leaf_id: req:A.5.6:sig_engagement_review
control_ref: A.5.6
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 2
---

# Periodic SIG Engagement Review

> Periodic check that memberships are still earning their place. Each entry is reviewed for value delivered, currency of contact, and continued relevance against the risk-topic scope. Dormant memberships are pruned; gaps where a new SIG should be joined are flagged

> **Replace each blank fill-in marker with your content. Leave the MUST and SHOULD heading markers untouched — they bind this document to the checklist when you upload it back.**

## 1. Review date within the planned interval

<<MUST item:A.5.6:rev_date>>
_Why: 27002:5.6 — maintain_

<<TEXT>>

## 2. Reviewer identity and role recorded

<<MUST item:A.5.6:rev_reviewer>>
_Why: Accountability_

<<TEXT>>

## 3. Per-entry outcome (continue / disengage / upgrade) with value-delivered notes (intel received, contributions made)

<<MUST item:A.5.6:rev_per_entry>>
_Why: 27002:5.6 — appropriate_

<<TEXT>>

## 4. Cross-check against the risk-topic scope — any new threat or domain that should add a SIG

<<MUST item:A.5.6:rev_scope_check>>
_Why: Cross-leaf coherence_

<<TEXT>>

## 5. Changes propagated back to the register

<<MUST item:A.5.6:rev_register_update>>
_Why: Closes the loop_

<<TEXT>>

---

## Recommended additions

_The items below strengthen the artefact but are not strictly required for the MUST checks. Fill in any that apply to your environment._

### 1. Ad-hoc review triggers listed (key representative departure, new threat class, budget cycle)

<<SHOULD item:A.5.6:rev_ad_hoc_triggers>>
_Why: Change-driven review_

<<TEXT>>

### 2. Next planned review date stated

<<SHOULD item:A.5.6:rev_next_date>>
_Why: Planning_

<<TEXT>>
