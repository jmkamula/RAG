---
leaf_id: req:Art.41:monitoring_program_review
control_ref: Art.41
standard_id: GDPR:2016/679
evidence_type: review_record
trigger_type: profile_fact
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Code Monitoring Program Review

> Annual verification — accreditation current, monitoring activities on cadence, infringement actions defensible (freshness=365)

<!-- TABLE-COLUMNS leaf:req:Art.41:monitoring_program_review -->
<!-- column: item:Art.41:rev_date -->
<!-- column: item:Art.41:rev_reviewer -->
<!-- column: item:Art.41:rev_accreditation_currency -->
<!-- column: item:Art.41:rev_monitoring_cadence -->
<!-- column: item:Art.41:rev_action_quality -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:Art.41:monitoring_program_review -->
| Rev Date | Rev Reviewer | Rev Accreditation Currency | Rev Monitoring Cadence | Rev Action Quality |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:Art.41:monitoring_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:Art.41:rev_date>>
_Why: Periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:Art.41:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (executive sponsor + independent counsel)

### Rev Accreditation Currency

<<MUST item:Art.41:rev_accreditation_currency>>
_Why: Art.41.1_

> _Standard text:_ Accreditation currency — SA accreditation still in force

### Rev Monitoring Cadence

<<MUST item:Art.41:rev_monitoring_cadence>>
_Why: Art.41.2_

> _Standard text:_ Monitoring cadence audit — every adherent assessed per procedure

### Rev Action Quality

<<MUST item:Art.41:rev_action_quality>>
_Why: Art.41.4_

> _Standard text:_ Action quality — corrective / suspension / exclusion decisions defensible vs procedure

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:Art.41:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
