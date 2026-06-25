---
leaf_id: req:7.4:communication_program_review
control_ref: 7.4
standard_id: ISO27001:2022
evidence_type: review_record
trigger_type: universal
freshness_days: 365
template_version: 1
must_count: 5
should_count: 1
table_shape: true
---

# Communication Program Review

> Annual verification that planned communications happened on cadence, the register is complete, regulator-mandated comms met their deadlines (freshness=365)

<!-- TABLE-COLUMNS leaf:req:7.4:communication_program_review -->
<!-- column: item:7.4:rev_date -->
<!-- column: item:7.4:rev_reviewer -->
<!-- column: item:7.4:rev_cadence_check -->
<!-- column: item:7.4:rev_mandated_deadlines -->
<!-- column: item:7.4:rev_audience_coverage -->
<!-- /TABLE-COLUMNS -->

## Register

Fill one row per record. Each column maps to a MUST item the auditor will check — empty columns count as unsatisfied. Add as many rows as you need.

<!-- EDIT-ZONE-START leaf:req:7.4:communication_program_review -->
| Rev Date | Rev Reviewer | Rev Cadence Check | Rev Mandated Deadlines | Rev Audience Coverage |
|---|---|---|---|---|
|          |          |          |          |          |
|          |          |          |          |          |
|          |          |          |          |          |
<!-- EDIT-ZONE-END leaf:req:7.4:communication_program_review -->

## Column guidance — what to fill in

### Rev Date

<<MUST item:7.4:rev_date>>
_Why: Clause 7.4 — periodic_

> _Standard text:_ Review date within the planned interval

### Rev Reviewer

<<MUST item:7.4:rev_reviewer>>
_Why: Accountability_

> _Standard text:_ Reviewer identity (ISMS Manager + comms lead)

### Rev Cadence Check

<<MUST item:7.4:rev_cadence_check>>
_Why: Effectiveness_

> _Standard text:_ Cadence check — planned communications actually delivered on time

### Rev Mandated Deadlines

<<MUST item:7.4:rev_mandated_deadlines>>
_Why: Compliance currency_

> _Standard text:_ Mandated deadlines check — every regulator-mandated comm met its SLA

### Rev Audience Coverage

<<MUST item:7.4:rev_audience_coverage>>
_Why: Cross-leaf coherence_

> _Standard text:_ Audience coverage check — every in-scope audience reached for required topics

---

## Recommended additional columns

_These columns strengthen the register but are not strictly required for the MUST checks. Add them to the table if they apply to your environment._

### Rev Next Date

<<SHOULD item:7.4:rev_next_date>>
_Why: Planning_

> _Standard text:_ Next planned review date stated
