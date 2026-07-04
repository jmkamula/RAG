---
leaf_id: req:B.8.3.1:program_review
control_ref: B.8.3.1
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Support Program Review

> Annual verification — technical support paths current, SLAs met, gaps in support matrix identified (freshness=365)

<!-- TABLE-COLUMNS leaf:req:B.8.3.1:program_review -->
<!-- column: item:B.8.3.1:rev_date -->
<!-- column: item:B.8.3.1:rev_reviewer -->
<!-- column: item:B.8.3.1:rev_path_currency -->
<!-- column: item:B.8.3.1:rev_sla_audit -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:B.8.3.1:program_review -->
| Rev Date | Rev Reviewer | Rev Path Currency | Rev Sla Audit |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:B.8.3.1:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:B.8.3.1:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:B.8.3.1:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (DPO + Product + Trust)

### Rev Path Currency

<<MUST item:B.8.3.1:rev_path_currency>>
_Why: §8.3.1_

> _Standard text:_ Support-path currency — technical paths remain functional after product changes

### Rev Sla Audit

<<MUST item:B.8.3.1:rev_sla_audit>>
_Why: Timeliness_

> _Standard text:_ SLA audit — support responses measured against contract SLAs

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:B.8.3.1:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
