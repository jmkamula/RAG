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
table_shape: true
---

# Periodic SIG Engagement Review

> Periodic check that memberships are still earning their place. Each entry is reviewed for value delivered, currency of contact, and continued relevance against the risk-topic scope. Dormant memberships are pruned; gaps where a new SIG should be joined are flagged

<!-- TABLE-COLUMNS leaf:req:A.5.6:sig_engagement_review -->
<!-- column: item:A.5.6:rev_date -->
<!-- column: item:A.5.6:rev_reviewer -->
<!-- column: item:A.5.6:rev_per_entry -->
<!-- column: item:A.5.6:rev_scope_check -->
<!-- column: item:A.5.6:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.5.6:sig_engagement_review -->
| Rev Date | Rev Reviewer | Rev Per Entry | Rev Scope Check | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.5.6:sig_engagement_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.5.6:rev_date>>
_Why: 27002:5.6 — maintain_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.5.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded

### Rev Per Entry

<<MUST item:A.5.6:rev_per_entry>>
_Why: 27002:5.6 — appropriate_

> _Standard text:_ Per-entry outcome (continue / disengage / upgrade) with value-delivered notes (intel received, contributions made)

### Rev Scope Check

<<MUST item:A.5.6:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the risk-topic scope — any new threat or domain that should add a SIG

### Rev Register Update

<<MUST item:A.5.6:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the register

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.5.6:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (key representative departure, new threat class, budget cycle)

### Rev Next Date

<<SHOULD item:A.5.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
