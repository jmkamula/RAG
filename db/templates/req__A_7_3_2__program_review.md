---
leaf_id: req:A.7.3.2:program_review
control_ref: A.7.3.2
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Notice Content Program Review

> Annual verification — notices reflect current processing state, field coverage complete per context, updates issued on time (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.3.2:program_review -->
<!-- column: item:A.7.3.2:rev_date -->
<!-- column: item:A.7.3.2:rev_reviewer -->
<!-- column: item:A.7.3.2:rev_currency_audit -->
<!-- column: item:A.7.3.2:rev_field_completeness -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.3.2:program_review -->
| Rev Date | Rev Reviewer | Rev Currency Audit | Rev Field Completeness |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.3.2:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.3.2:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.3.2:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Legal + UX)

### Rev Currency Audit

<<MUST item:A.7.3.2:rev_currency_audit>>
_Why: §7.3.2 — updated information_

> _Standard text:_ Currency audit — sampled notices verified against A.7.2.1 purpose register + A.7.2.8 RoPA

### Rev Field Completeness

<<MUST item:A.7.3.2:rev_field_completeness>>
_Why: §7.3.2 — type of information_

> _Standard text:_ Field completeness — sampled notices verified against catalog

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.3.2:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
