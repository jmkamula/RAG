---
leaf_id: req:A.7.3.4:program_review
control_ref: A.7.3.4
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Withdrawal Program Review

<<DOC_CONTROL>>

> Annual verification — withdrawal channels functional, propagation reliable, SLA met, no consent-basis activity without a corresponding withdrawal path (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.4:program_review -->
<!-- column: item:A.7.3.4:rev_date -->
<!-- column: item:A.7.3.4:rev_reviewer -->
<!-- column: item:A.7.3.4:rev_channel_test -->
<!-- column: item:A.7.3.4:rev_propagation_audit -->
<!-- /TABLE-COLUMNS -->

## What this template gives you

This template helps you document and review your withdrawal channels, ensuring they work properly, meet service commitments, and that users can always withdraw consent where required.

## When to use it

Use this template if your organization handles personal data and needs to verify, about once a year, that all withdrawal processes are reliable and compliant with privacy standards.

## Prerequisites
<<PREREQUISITES>>

## Cross-references

<<CROSS_REFERENCES>>

## Estimated effort

Expect to spend about 40 to 60 minutes completing this from scratch, depending on how many withdrawal channels you need to review and document.

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.4:program_review -->
| Rev Date | Rev Reviewer | Rev Channel Test | Rev Propagation Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.4:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.4:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

<<GUIDANCE>>

### Rev Reviewer

<<MUST item:A.7.3.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Engineering)

<<GUIDANCE>>

### Rev Channel Test

<<MUST item:A.7.3.4:rev_channel_test>>
_Why: §7.3.4 — mechanism_

> _Standard text:_ Channel test — end-to-end withdrawal test per channel

<<GUIDANCE>>

### Rev Propagation Audit

<<MUST item:A.7.3.4:rev_propagation_audit>>
_Why: §7.3.4 — dissemination_

> _Standard text:_ Propagation audit — sampled withdrawals verified to have stopped downstream processing + notified third parties

---

<<GUIDANCE>>

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated

<<GUIDANCE>>

## Revision history

<<REVISION_HISTORY>>
