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

<<DOC_CONTROL>>

> Periodic check that memberships are still earning their place. Each entry is reviewed for value delivered, currency of contact, and continued relevance against the risk-topic scope. Dormant memberships are pruned; gaps where a new SIG should be joined are flagged

<!-- TABLE-COLUMNS leaf:req:A.5.6:sig_engagement_review -->
<!-- column: item:A.5.6:rev_date -->
<!-- column: item:A.5.6:rev_reviewer -->
<!-- column: item:A.5.6:rev_per_entry -->
<!-- column: item:A.5.6:rev_scope_check -->
<!-- column: item:A.5.6:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you regularly review and document the value and relevance of your memberships in Special Interest Groups (SIGs), ensuring each one continues to support your organization's risk and compliance needs.

## When to use it

Use this review record once a year to check all your SIG memberships, confirming they are still active, valuable, and aligned with your current risk topics. It's a good fit if you want to keep your memberships purposeful and up to date.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 10 to 15 minutes per required element for each SIG entry. Completing the full register from scratch will likely take 1 to 2 hours, depending on the number of memberships you have.

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

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.5.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity and role recorded

<<GUIDANCE>>

### Rev Per Entry

<<MUST item:A.5.6:rev_per_entry>>
_Why: 27002:5.6 — appropriate_

> _Standard text:_ Per-entry outcome (continue / disengage / upgrade) with value-delivered notes (intel received, contributions made)

<<GUIDANCE>>

### Rev Scope Check

<<MUST item:A.5.6:rev_scope_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Cross-check against the risk-topic scope — any new threat or domain that should add a SIG

<<GUIDANCE>>

### Rev Register Update

<<MUST item:A.5.6:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated back to the register

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Ad Hoc Triggers

<<SHOULD item:A.5.6:rev_ad_hoc_triggers>>
_Why: Change-driven review_

> _Standard text:_ Ad-hoc review triggers listed (key representative departure, new threat class, budget cycle)

<<GUIDANCE>>

### Rev Next Date

<<SHOULD item:A.5.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
