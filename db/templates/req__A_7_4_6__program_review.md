---
leaf_id: req:A.7.4.6:program_review
control_ref: A.7.4.6
standard_id: ISO27701:2019
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 4
should_count: 1
table_shape: true
---

# Temp Files Program Review

> Annual verification — sweep cadence honoured, disposal periods respected, anomalies investigated, no orphan temp files hanging around (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4.6:program_review -->
<!-- column: item:A.7.4.6:rev_date -->
<!-- column: item:A.7.4.6:rev_reviewer -->
<!-- column: item:A.7.4.6:rev_sweep_health -->
<!-- column: item:A.7.4.6:rev_orphan_sample -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4.6:program_review -->
| Rev Date | Rev Reviewer | Rev Sweep Health | Rev Orphan Sample |
|---|---|---|---|
|          |          |          |          |
|          |          |          |          |
|          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4.6:program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4.6:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.4.6:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Infrastructure + DPO)

### Rev Sweep Health

<<MUST item:A.7.4.6:rev_sweep_health>>
_Why: §7.4.6 — periodic checks_

> _Standard text:_ Sweep health — cadence honoured, coverage complete

### Rev Orphan Sample

<<MUST item:A.7.4.6:rev_orphan_sample>>
_Why: Effectiveness_

> _Standard text:_ Orphan-file sample check — random directories checked for temp files past retention

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4.6:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
