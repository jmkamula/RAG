---
leaf_id: req:A.7.3.3:program_review
control_ref: A.7.3.3
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Notice Delivery Program Review

> Annual verification — notices reachable at every touchpoint, plain-language standard maintained, no delivery gaps (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.3:program_review -->
<!-- column: item:A.7.3.3:rev_date -->
<!-- column: item:A.7.3.3:rev_reviewer -->
<!-- column: item:A.7.3.3:rev_reachability_audit -->
<!-- column: item:A.7.3.3:rev_plain_language_audit -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.3:program_review -->
| Rev Date | Rev Reviewer | Rev Reachability Audit | Rev Plain Language Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.3:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.3:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.3.3:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Product + UX)

### Rev Reachability Audit

<<MUST item:A.7.3.3:rev_reachability_audit>>
_Why: §7.3.3 — permanently accessible_

> _Standard text:_ Reachability audit — sampled touchpoints verified to serve current notice

### Rev Plain Language Audit

<<MUST item:A.7.3.3:rev_plain_language_audit>>
_Why: §7.3.3 — clear plain language_

> _Standard text:_ Plain-language audit — sampled notices reviewed against readability target

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.3:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
