---
leaf_id: req:A.7.4:monitoring_program_review
control_ref: A.7.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Periodic Monitoring Program Review

> Annual verification that monitoring is effective (alarms responded to within SLA, anomalies investigated, footage retained correctly). Annual cadence (freshness=365)

<!-- TABLE-COLUMNS leaf:req:A.7.4:monitoring_program_review -->
<!-- column: item:A.7.4:rev_date -->
<!-- column: item:A.7.4:rev_reviewer -->
<!-- column: item:A.7.4:rev_response_sla -->
<!-- column: item:A.7.4:rev_coverage_check -->
<!-- column: item:A.7.4:rev_register_update -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:A.7.4:monitoring_program_review -->
| Rev Date | Rev Reviewer | Rev Response Sla | Rev Coverage Check | Rev Register Update |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:A.7.4:monitoring_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:A.7.4:rev_date>>
_Why: 27002:7.4 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:A.7.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (Facilities + SOC + InfoSec)

### Rev Response Sla

<<MUST item:A.7.4:rev_response_sla>>
_Why: 27002:7.4 — alert response_

> _Standard text:_ Response-SLA analysis (alarm-to-on-site arrival times measured against SLA)

### Rev Coverage Check

<<MUST item:A.7.4:rev_coverage_check>>
_Why: Cross-leaf coherence_

> _Standard text:_ Coverage check — blind spots remediated? new areas brought into monitoring scope?

### Rev Register Update

<<MUST item:A.7.4:rev_register_update>>
_Why: Closes the loop_

> _Standard text:_ Changes propagated to the procedure / scope

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:A.7.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
