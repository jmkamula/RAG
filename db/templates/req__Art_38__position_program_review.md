---
leaf_id: req:Art.38:position_program_review
control_ref: Art.38
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# DPO Position Program Review

> Annual verification — DPO position guarantees actually upheld (involvement, resources, independence, no COI) (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.38:position_program_review -->
<!-- column: item:Art.38:rev_date -->
<!-- column: item:Art.38:rev_reviewer -->
<!-- column: item:Art.38:rev_involvement_audit -->
<!-- column: item:Art.38:rev_independence_audit -->
<!-- column: item:Art.38:rev_coi_recheck -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.38:position_program_review -->
| Rev Date | Rev Reviewer | Rev Involvement Audit | Rev Independence Audit | Rev Coi Recheck |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.38:position_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.38:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.38:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (executive sponsor + non-executive director / external counsel if available)

### Rev Involvement Audit

<<MUST item:Art.38:rev_involvement_audit>>
_Why: Art.38.1_

> _Standard text:_ Involvement audit — DPO invited to all in-scope forums; not bypassed on data-protection decisions

### Rev Independence Audit

<<MUST item:Art.38:rev_independence_audit>>
_Why: Art.38.3_

> _Standard text:_ Independence audit — no recorded instructions on tasks; no dismissal pressure

### Rev Coi Recheck

<<MUST item:Art.38:rev_coi_recheck>>
_Why: Art.38.6_

> _Standard text:_ COI recheck — DPO role assignments still free of conflicts

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.38:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
